import asyncio
import base64
import json
import os
import subprocess
import sys
import aiohttp
import re

BASE = "https://api.renderflux.com/"
JOB_SEARCH_WAIT = 5
JOB_FAIL_WAIT = 5
PROGRESS_INTERVAL = 120

async def fetch_job():
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(f"{BASE}batches/next") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    await asyncio.sleep(JOB_SEARCH_WAIT)

def construct_cmd(job, _id):
    args = ["python disco.py"]

    args.append("--text_prompt \"{\\\"0\\\": [\\\""+job['prompt']+"\\\"]}\"")
    args.append(f"--width_height \"[{job['width']}, {job['height']}]\"")
    args.append(f"--batch_name {_id}")
    args.append("--n_batches=1")
    args.append("--display_rate=5")
    args.append(f"--steps={job['steps']}")

    for model, value in job['models'].items():
        args.append(f"--{model} {value}")

    args.append(f"--eta={job['eta']}")
    args.append(f"--clip_guidance_scale={job['clip_guidance_scale']}")
    args.append(f"--diffusion_model={job['diffusion_model']}")
    args.append(f"--clamp_max={job['clamp_max']}")
    args.append(f"--cut_ic_pow={job['cut_ic_pow']}")
    args.append(f"--cutn_batches={job['cutn_batches']}")
    args.append(f"--sat_scale={job['sat_scale']}")
    args.append(f"--set_seed={job['seed']}")
    args.append(f"--cut_innercut={job['cut_innercut']}")
    args.append(f"--cut_overview={job['cut_overview']}")
    args.append(f"--use_secondary_model={job['use_secondary_model']}")

    return " ".join(args)

async def update_job_progress(job, process):

    filename = f"images_out/{job['_id']}/progress.png"

    while True:
        await asyncio.sleep(PROGRESS_INTERVAL)
        # get the most recent line of the process's stdout without waiting for it to finish

        print(f"Getting progress...")

        progress = 0
        progress_filename = f"images_out/{job['_id']}/progress_data.txt"
        if not os.path.exists(progress_filename):
            print(f"Progress file not found: {progress_filename}")
        else:
            with open(progress_filename, "r+") as f:
                data = f.read()
                js = json.loads(data if data else "{}")
                progress = js.get("percent", 0)

        # old stuff from trying to get the ETA and etc from stdout PIPE but it didn't work and I don't know why
        # if line:
        #     print(f"Got line: {line}")

        #     match = re.search(r"([0-9]+)\/([0-9]+) \[([0-9]+):([0-9]+)<([0-9]+):([0-9]+), ([0-9.]+)it\/s\]", line)
        #     if match:
        #         progress = int(match.group(1)) / int(match.group(2))
        #         print(f"Got progress: {progress}")

        # check if file exists
        if not os.path.isfile(filename):
            print(f"Progress file {filename} does not exist yet...")
            continue

        async with aiohttp.ClientSession() as session:

            json = {
                "progress": progress,
                "image": base64.b64encode(open(filename, "rb").read()).decode("utf-8")
            }

            async with session.post(f"{BASE}jobs/{job['_id']}/progress", json=json) as resp:
                if resp.status != 200:
                    print(f"Error sending progress data to API...")
                    await asyncio.sleep(JOB_FAIL_WAIT)
                    continue
                print(f"Sent progress data to API...")
        

async def run_job():
    job = await fetch_job()

    print(f"Got job: {job.get('_id')}")
    
    cmd = construct_cmd(job['settings'], job.get('_id'))
    process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"Spawned process: {cmd}")

    progress_task = asyncio.create_task(update_job_progress(job, process))
    print(f"Spawned progress task...")

    await process.wait()

    progress_task.cancel()

    if process.returncode != 0:
        print(f"Error with job...")

        print(f"Stdout: {(await process.stdout.read()).decode('utf-8')}")
        print(f"Stderr: {(await process.stderr.read()).decode('utf-8')}")

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE}jobs/{job['_id']}/fail", json={"error": "job failed"}) as resp:
                if resp.status != 200:
                    print(f"Error sending fail data to API... {resp.status}: {await resp.text()}")
                    await asyncio.sleep(JOB_FAIL_WAIT)
                    return
                print(f"Sent fail data to API...")

        await asyncio.sleep(JOB_FAIL_WAIT)
        return

    json = {
        "image": base64.b64encode(open(f"images_out/{job['_id']}/{job['_id']}(0)_0.png", "rb").read()).decode("utf-8")
    }

    # send the file data to the API when the job completes
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE}jobs/{job['_id']}/complete", json=json) as resp:
            if resp.status != 200:
                print(f"Error sending file data to API...")
                await asyncio.sleep(JOB_FAIL_WAIT)
                return
            print(f"Sent file data to API...")


async def main():
    while True:
        try:
            await run_job()
        except Exception as e:
            print(e)
            await asyncio.sleep(JOB_FAIL_WAIT)


if __name__ == "__main__":
    asyncio.run(main())