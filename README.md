Advantage Air API Wrapper

# Get
Returns the current state of all components.
> async_get()

# Set
Change attributes by sending the updated values to the relevant endpoint.
> aircon.async_set()
> lights.async_set()
> things.async_set()

# Example
~~~~{.python}
import asyncio
import aiohttp
from advantage_air import advantage_air

async def main():
    async with aiohttp.ClientSession() as session:
        aa = advantage_air("192.168.100.100",port=2025,session=session,retry=5)
        if(await aa.async_get(1)):
            print(await aa.aircon.async_get())
            print(await aa.async_set({}))

asyncio.run(main())
~~~~