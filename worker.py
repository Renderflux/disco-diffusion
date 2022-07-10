import asyncio
import aiohttp

BASE = "https://api.renderflux.com/"
JOB_SEARCH_WAIT = 5
JOB_FAIL_WAIT = 5

async def fetch_job():
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(f"{BASE}batches/next") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    await asyncio.sleep(JOB_SEARCH_WAIT)

def construct_cmd(job):
    args = ""

    args += " --text_prompt \"{\\\"0\\\": \\\"" + job['prompt'] + "\\\"}\""
    args += f" --width_height [{job['width']}, {job['height']}]"
    args += f" --batch_name {job['_id']}"
    args += " --n_batches=1"

    return f"python disco.py{args}"

async def run_job():
    job = await fetch_job()

    cmd = construct_cmd(job)

    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await process.wait()

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