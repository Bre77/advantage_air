Advantage Air API Wrapper

~~~~{.python}
import asyncio
from advantage_air import advantage_air

aa = advantage_air("192.168.100.24")

async def main():
    if(await aa.async_get(1)):
        print(await aa.async_get())
        print(await aa.async_change({}))

asyncio.run(main())
~~~~