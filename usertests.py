import asyncio
import aiohttp
from advantage_air import advantage_air

target = input("Enter the IP or hostname of your Advantage Air tablet: ")

async def main():
    async with aiohttp.ClientSession() as session:
        aa = advantage_air(target,port=2025,session=session,retry=5)

        print("> Auto Fan Test")
        print()

        # Get data
        data = await aa.async_get()
        for ac in data['aircons']:
            print(ac, "fan is", data['aircons'][ac]['info']['fan'])
        

        # Set to auto
        for ac in data['aircons']:
            data['aircons']
        print(ac, "change", await aa.async_change({
            ac: {
                'info': {
                    'fan': 'auto'
                }
            }
        }))

        # Get data
        data = await aa.async_get()
        for ac in data['aircons']:
            print(ac, "fan is", data['aircons'][ac]['info']['fan'])

asyncio.run(main())