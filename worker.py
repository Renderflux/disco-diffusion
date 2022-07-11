import asyncio
import subprocess
import sys
import aiohttp

BASE = "https://api.renderflux.com/"
JOB_SEARCH_WAIT = 5
JOB_FAIL_WAIT = 5
PROGRESS_INTERVAL = 60

async def fetch_job():
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(f"{BASE}batches/next") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    await asyncio.sleep(JOB_SEARCH_WAIT)

def construct_cmd(job):
    args = ["python disco.py"]

    args.append("--text_prompt \"{\\\"0\\\": \\\"" + job['prompt'] + "\\\"}\"")
    args.append(f"--width_height [{job['width']}, {job['height']}]")
    args.append(f"--batch_name {job['_id']}")
    args.append("--n_batches=1")
    args.append(f"--steps={job['steps']}")
    args.append(f"--{job['model']} true")
    args.append(f"--clip_guidance_scale={job['clip_guidance_scale']}")
    args.append(f"--diffusion_model={job['diffusion_model']}")
    args.append(f"--clamp_max={job['clamp_max']}")
    args.append(f"--cut_ic_pow={job['cut_ic_pow']}")
    args.append(f"--cutn_batches={job['cutn_batches']}")
    args.append(f"--sat_scale={job['sat_scale']}")
    args.append(f"--set_seed={job['seed']}")
    args.append(f"--cut_innercut={job['cut_innercut']}")
    args.append(f"--cut_overview={job['cut_overview']}")

    return " ".join(args)

async def update_job_progress(job):
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE}batches/{job['_id']}/progress", data=open(f"/workspace/images_out/{job['_id']}/progress.png", "rb")) as resp:
                if resp.status != 200:
                    print(f"Error sending progress data to API...")
                    await asyncio.sleep(JOB_FAIL_WAIT)
                    return
                print(f"Sent progress data to API...")
        await asyncio.sleep(PROGRESS_INTERVAL)

async def run_job():
    job = await fetch_job()

    progress_task = asyncio.create_task(update_job_progress(job))
    
    cmd = construct_cmd(job)
    process = asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    await process.wait()

    progress_task.cancel()

    if process.returncode != 0:
        print(f"Error with job...")
        await asyncio.sleep(JOB_FAIL_WAIT)
        return

    filepath = f"/workspace/images_out/{job['_id']}/{job['_id']}(0)_0.png"

    # send the file data to the API when the job completes
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE}batches/{job['_id']}/complete", data=open(filepath, "rb")) as resp:
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