import asyncio
import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            print("Start")
            async with session.get("http://192.168.100.24:2025/getSystemData") as resp:
                await resp.json(content_type=None)
                await asyncio.sleep(20)


asyncio.run(main())
