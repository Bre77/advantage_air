Advantage Air API Wrapper

~~~~{.python}
import asyncio
import aiohttp
from advantage_air import advantage_air

async def main():
    async with aiohttp.ClientSession() as session:
        aa = advantage_air("192.168.100.24",port=2025,session=session,retry=5)
        if(await aa.async_get(1)):
            print(await aa.async_get())
            print(await aa.async_change({}))

asyncio.run(main())
~~~~