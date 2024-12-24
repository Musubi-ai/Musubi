import aiohttp
import asyncio
import time


async def do(num):
    print(f"Hello, {num}")
    await asyncio.sleep(1)
    print(f"world, {num}")


if __name__ == "__main__":
    start = time.time()
    task = [do(i) for i in range(5)]
    asyncio.run(asyncio.wait(task))
    end = time.time()
    print(f'花費時間：{end-start}')