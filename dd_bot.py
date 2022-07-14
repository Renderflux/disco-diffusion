import sys
import json
from loguru import logger
import os
import subprocess
import requests
import dd
import math
import time
import traceback
from yaml import dump, full_load

# Error handler
class RestartException(Exception):
    def __init__(self, error):
        self.error = error


class CancelException(Exception):
    def __init__(self, error):
        self.error = error


def upload_progress(preview_url, args):
    try:
        fn = f"{args.batchFolder}/progress.png"
        files = {"file": open(fn, "rb")}
        logger.info(f"Uploaded {fn}...")
        r = requests.post(preview_url, files=files)
    except:
        logger.error("DD Bot error.  Continuing...")
        pass


def ack_instructions(instructions_url, instructions):
    r = requests.delete(instructions_url)
    return r


def abandon_job(args):
    abandon_url = f"{args.dd_bot_url}/abandonjob/{args.dd_bot_agentname}"
    try:
        r = requests.get(abandon_url).json()
        logger.info("Job abandoned.")
    except:
        logger.info("Abandon timed out.")
        r = None
    return r


def get_instructions(instructions_url, args):
    r = requests.get(instructions_url)
    ins = r.json()
    if ins:
        if "command" in ins:
            command = ins["command"]
            logger.info(f"👉 Instructions: {command}")
            # Restart
            if command == "restart":
                logger.info("🔃 Restarting...")
                ack_instructions(instructions_url, ins)
                raise RestartException(ins)
            # Abandon Job
            if command == "abandon":
                logger.info("🔃 Abandoning job...")
                ack_instructions(instructions_url, ins)
                abandon_job(args)
                raise CancelException(ins)

    return ins


def update_progress(progress_url, percent, device, prev_ts):
    n = time.time()
    update = True
    if prev_ts:
        duration = n - prev_ts
        if duration < 15:
            update = False
    else:
        prev_ts = n

    if update:
        try:
            cd = device
            smi = f"nvidia-smi --query-gpu=gpu_name,temperature.gpu,utilization.gpu,utilization.memory,memory.used --format=csv,noheader,nounits -i {str(device).split(':')[1]}"
            gpustats = subprocess.run(smi.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
            # logger.info(f"🌍 Updating progress to {progress_url}")
            r = requests.post(progress_url, data={"percent": percent, "gpustats": gpustats})
        except Exception as e:
            logger.error(f"DD Bot error.  Continuing...\n{e}")
            pass
        return n
    else:
        return prev_ts


def bot_loop(args, folders, frame_num, clip_models, init_scale, skip_steps, secondary_model, lpips_model, midas_model, midas_transform, device):
    POLL_INTERVAL = 5
    progress_url = f"{args.dd_bot_url}/progress/{args.dd_bot_agentname}/{args.batch_name}"
    logger.info(f"Discord Bot mode enabled: {progress_url}")
    smi = f"nvidia-smi --query-gpu=gpu_name,temperature.gpu,utilization.gpu,utilization.memory,memory.used --format=csv,noheader,nounits -i {str(device).split(':')[1]}"
    gpustats = subprocess.run(smi.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
    logger.info(str(device))
    run = True
    idle_time = 0
    while run == True:
        connected = False
        url = f"{args.dd_bot_url}/takeorder/{args.dd_bot_agentname}"
        try:
            logger.debug(f"🌎 Checking '{url}'")
            my_model = None
            # if args.ViTB32 and args.ViTB16 and args.RN50:
            #     my_model = "default"
            # if args.ViTB32 and args.ViTB16 and args.ViTL14:
            #     my_model = "vitl14"
            # if args.ViTB32 and args.ViTB16 and args.ViTL14_336:
            #     my_model = "vitl14x336"
            # if args.ViTB32 and args.ViTB16 and args.RN50x64:
            #     my_model = "rn50x64"
            # if args.ViTB32 and args.ViTB16 and args.RN50x64 and args.ViTL14_336:
            #     my_model = "ludicrous"

            my_model = "custom"

            bot_config = {
                "bot_version": 2.2,
                "idle_time": idle_time,
                "model": my_model,
                "clip_models": json.dumps(
                    {
                        "ViTB16": args.ViTB16,
                        "ViTB32": args.ViTB32,
                        "RN50": args.RN50,
                        "RN50x4": args.RN50x4,
                        "RN50x16": args.RN50x16,
                        "RN50x64": args.RN50x64,
                        "ViTL14": args.ViTL14,
                        "ViTL14_336": args.ViTL14_336,
                        "RN101": args.RN101,
                    }
                ),
            }
            logger.info(bot_config)
            results = requests.post(
                url,
                data=bot_config,
            ).json()

            if results["success"]:
                idle_time = 0
                connected = True
                logger.info(results["details"])
                tp = results["details"]["text_prompt"]
                tp = tp.replace("“", '"')
                tp = tp.replace("”", '"')
                # Attempt to accept JSON Structured Text Prompt...
                try:
                    tp = eval(tp)
                    if type(tp) == list:
                        prompts_series = {"0": tp}
                        logger.info("JSON structured text prompt found.")
                    else:
                        raise Exception("Non-list item found")
                except:
                    tp = results["details"]["text_prompt"]
                    tp = tp.replace(":", "")
                    tp = tp.replace('"', "")
                    prompts_series = {"0": [tp]}
                    logger.info("Flat string text prompt found.")

                steps = results["details"]["steps"]
                uuid = results["details"]["uuid"]
                shape = results["details"]["shape"]

                clamp_max = float(results["details"]["clamp_max"])
                clip_guidance_scale = results["details"]["clip_guidance_scale"]
                cut_ic_pow = int(results["details"]["cut_ic_pow"])
                sat_scale = float(results["details"]["sat_scale"])
                try:
                    eta = float(results["details"]["eta"])
                except:
                    eta = 0.5
                try:
                    cutn_batches = int(results["details"]["cutn_batches"])
                except:
                    cutn_batches = 4
                try:
                    render_type = results["details"]["render_type"]
                except:
                    render_type = "render"
                try:
                    cut_schedule = results["details"]["cut_schedule"]
                except:
                    cut_schedule = "default"
                try:
                    set_seed = results["details"]["set_seed"]
                except:
                    set_seed = "random_seed"
                try:
                    symmetry = results["details"]["symmetry"]
                except:
                    symmetry = "no"
                try:
                    symmetry_loss_scale = int(results["details"]["symmetry_loss_scale"])
                except:
                    symmetry_loss_scale = 1500

                if not clamp_max:
                    clamp_max = 0.05

                if not clip_guidance_scale:
                    clip_guidance_scale = 1500

                if not cut_ic_pow:
                    cut_ic_pow = 1

                if not sat_scale:
                    sat_scale = 0

                if set_seed == -1:
                    set_seed = "random_seed"

                if not shape:
                    shape = "landscape"

                cut_overview = "[12]*400+[4]*600"
                cut_innercut = "[4]*400+[12]*600"

                if cut_schedule == "default":
                    cut_overview = "[12]*400+[4]*600"
                    cut_innercut = "[4]*400+[12]*600"

                if cut_schedule == "detailed-a":
                    cut_overview = "[10]*200+[8]*200+[6]*200+[2]*200+[2]*200"
                    cut_innercut = "[0]*200+[2]*200+[6]*200+[8]*200+[10]*200"

                if cut_schedule == "detailed-b":
                    cut_overview = "[10]*200+[8]*200+[6]*200+[4]*200+[2]*200"
                    cut_innercut = "[2]*200+[2]*200+[8]*200+[8]*200+[10]*200"

                if cut_schedule == "ram_efficient":
                    cut_overview = "[10]*200+[8]*200+[5]*200+[2]*200+[2]*200"
                    cut_innercut = "[0]*200+[2]*200+[5]*200+[7]*200+[9]*200"

                if cut_schedule == "potato":
                    cut_overview = "[1]*1000"
                    cut_innercut = "[1]*1000"

                if render_type == "sketch":
                    if shape == "landscape":
                        w_h = [640, 512]
                    if shape == "portrait":
                        w_h = [512, 640]
                    if shape == "square":
                        w_h = [512, 512]
                    if shape == "pano":
                        w_h = [1024, 256]
                    if shape == "skyscraper":
                        w_h = [256, 1024]
                    if shape == "tiny-square":
                        w_h = [256, 256]
                else:
                    if shape == "landscape":
                        w_h = [1280, 768]
                    if shape == "portrait":
                        w_h = [768, 1280]
                    if shape == "square":
                        w_h = [1024, 1024]
                    if shape == "pano":
                        w_h = [2048, 512]
                    if shape == "skyscraper":
                        w_h = [512, 2048]
                    if shape == "tiny-square":
                        w_h = [512, 512]

                if symmetry == "yes":
                    args.symmetry_loss = True
                    args.symmetry_switch = math.floor(int(steps) / 2)
                    args.symmetry_loss_scale = symmetry_loss_scale

                if cut_schedule != "default":
                    args.cut_overview = cut_overview
                    args.cut_innercut = cut_innercut

                args.batch_name = uuid
                args.steps = int(steps)
                args.set_seed = set_seed
                args.n_batches = 1
                args.steps = steps
                args.clamp_max = clamp_max
                args.cutn_batches = cutn_batches
                args.eta = eta
                args.clip_guidance_scale = clip_guidance_scale
                args.cut_ic_pow = cut_ic_pow
                args.sat_scale = sat_scale
                args.width_height = w_h
                args.prompts_series = prompts_series
                args.text_prompts = prompts_series
                args.images_out = "images_out"
                args.init_images = "init_images"
                folders = dd.setupFolders(pargs=args, PROJECT_DIR=os.getcwd())
                args.batchFolder = folders.batch_folder
                args.batchNum = 0
                s = time.time()
                dd.disco(args, folders, frame_num, clip_models, init_scale, skip_steps, secondary_model, lpips_model, midas_model, midas_transform, device)
                e = time.time()
                duration = e - s
                fn = f"{folders.batch_folder}/{uuid}(0)_0.png"
                url = f"{args.dd_bot_url}/upload/{args.dd_bot_agentname}/{uuid}"
                files = {"file": open(fn, "rb")}
                values = {"duration": duration}
                logger.info(f"🌍 Uploading {fn} to {url}...")
                r = requests.post(url, files=files, data=values)
                dump(args.todict(), open(f"configs/{uuid}_gen.yaml", "w"))
                try:
                    # files = {"file": open(f"{folders.batch_folder}/{uuid}(0).log", "rb")}
                    # r = requests.post(f"{args.dd_bot_url}/uploadlog/{args.dd_bot_agentname}/{uuid}", files=files, data=values)
                    files = {"file": open(f"configs/{uuid}_gen.yaml", "rb")}
                    r = requests.post(f"{args.dd_bot_url}/uploadconfig/{args.dd_bot_agentname}/{uuid}", files=files, data=values)
                except Exception as e:
                    logger.error(e)
            else:
                logger.info(f"{results['message']}")
        except KeyboardInterrupt as kb:
            logger.info("Exiting...")
            run = False
        except RestartException as e:
            logger.info("🔃 Received Restart signal.")
            run = False
            return "🔃 Received Restart signal."
        except CancelException as e:
            logger.info("🔃 Abandon signal.")
        except Exception as e:
            if connected:
                tb = traceback.format_exc()
                logger.error(f"Bad job detected.\n\n{e}\n\n{tb}")
                values = {"message": f"Job failed:\n\n{e}", "traceback": tb}
                r = requests.post(f"{args.dd_bot_url}/reject/{args.dd_bot_agentname}/{uuid}", data=values)
            else:
                logger.error(f"Error.  Check your DD_URL and if the DD app is running at that location.  Also check your own internet connectivity.  Exception:\n{e}")
        finally:
            logger.info(f"Sleeping for {POLL_INTERVAL} seconds...  I've been sleeping for {idle_time} seconds.")
            idle_time = idle_time + POLL_INTERVAL
            time.sleep(POLL_INTERVAL)
