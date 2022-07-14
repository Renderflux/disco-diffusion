import math
from pkgutil import extend_path
import subprocess
from time import sleep
from loguru import logger
import requests
import json
import argparse
import os
from dotenv import load_dotenv
import time
import traceback


def loop(args=None):
    DD_URL = args.dd_url
    DD_NAME = args.agent
    DD_IMAGES_OUT = args.images_out
    DD_CUDA_DEVICE = args.cuda_device
    POLL_INTERVAL = args.poll_interval
    idle_time = 0
    run = True
    logger.info("Entering run loop...")
    while run == True:
        try:
            url = f"{DD_URL}/agent/{DD_NAME}"
            logger.debug(f"🌎 Checking for config: '{url}'")
            results = requests.get(url).json()

            model_mode = "default"
            if results:
                if "model_mode" in results:
                    model_mode = results["model_mode"]

            logger.info(f"Mode: {model_mode}")

            ViTB16 = False
            ViTB32 = False
            RN50 = False
            RN50x4 = False
            RN50x16 = False
            RN50x64 = False
            ViTL14 = False
            ViTL14_336 = False
            RN101 = False

            # Legacy preset model modes:
            if model_mode == "default":
                ViTB16 = True
                ViTB32 = True
                RN50 = True

            if model_mode == "vitl14":
                ViTB16 = True
                ViTB32 = True
                ViTL14 = True

            if model_mode == "vitl14_336":
                ViTB16 = True
                ViTB32 = True
                ViTL14_336 = True

            if model_mode == "rn50x64":
                ViTB16 = True
                ViTB32 = True
                RN50x64 = True

            if model_mode == "ludicrous":
                ViTB16 = True
                ViTB32 = True
                RN50x64 = True
                ViTL14_336 = True

            if model_mode == "custom":
                try:
                    ViTB16 = model_mode = results["clip_models"]["ViTB16"]
                    ViTB32 = results["clip_models"]["ViTB32"]
                    RN50 = results["clip_models"]["RN50"]
                    RN50x4 = results["clip_models"]["RN50x4"]
                    RN50x16 = results["clip_models"]["RN50x16"]
                    RN50x64 = results["clip_models"]["RN50x64"]
                    ViTL14 = results["clip_models"]["ViTL14"]
                    ViTL14_336 = results["clip_models"]["ViTL14_336"]
                    RN101 = results["clip_models"]["RN101"]
                except Exception as e:
                    logger.error(e)

            job = f"python disco.py --dd_bot=true --dd_bot_url={DD_URL} --dd_bot_agentname={DD_NAME} --batch_name={DD_NAME} --cuda_device={DD_CUDA_DEVICE} --images_out={DD_IMAGES_OUT} --ViTB16 {ViTB16} --ViTB32 {ViTB32} --RN50 {RN50} --RN50x4 {RN50x4} --RN50x16 {RN50x16} --RN50x64 {RN50x64} --ViTL14 {ViTL14} --ViTL14_336 {ViTL14_336} --RN101 {RN101}"

            try:
                s = time.time()
                logger.info(job)
                log = subprocess.run(job.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
                e = time.time()
                duration = e - s
                logger.info(f"Duration: {duration}")
            except KeyboardInterrupt:
                logger.info("Exiting...")
                run = False
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"Crash detected.\n\n{e}")
                values = {"message": f"Job failed:\n\n{e}", "traceback": tb, "log": log}
                logger.error(values)
            finally:
                logger.info(f"Sleeping for {POLL_INTERVAL} seconds...  I've been sleeping for {idle_time} seconds.")
                idle_time = idle_time + POLL_INTERVAL
                sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Exiting...")
            run = False
        except:
            logger.info("Problem getting config.")


def main():

    load_dotenv()
    parser = argparse.ArgumentParser(description="Disco Diffusion")
    parser.add_argument("--dd_url", help="Discord Bot http endpoint", required=False, default=os.getenv("DD_URL"))
    parser.add_argument("--agent", help="Your agent name", required=False, default=os.getenv("DD_NAME"))
    parser.add_argument("--images_out", help="Directory for render jobs", required=False, default=os.getenv("DD_IMAGES_OUT", "images_out"))
    parser.add_argument("--cuda_device", help="CUDA Device", required=False, default=os.getenv("DD_CUDA_DEVICE", "cuda:0"))
    parser.add_argument("--poll_interval", type=int, help="Polling interval between jobs", required=False, default=os.getenv("DD_POLL_INTERVAL", 5))
    parser.add_argument("--dream_time", type=int, help="Time in seconds until dreams", required=False, default=os.getenv("DD_POLL_INTERVAL", 300))
    args = parser.parse_args()
    loop(args)


if __name__ == "__main__":
    main()
