Advantage Air API Wrapper

# Get

Returns the current state of all components.

> async_get()

# Set

Change attributes by sending the updated values to the relevant endpoint.

## aircon.async_update_ac(ac: str, data: dict)

Update values on the AC system

## aircon.async_update_zone(ac: str, zone: str, data: dict)

Update values on a specific zone

## lights.async_update_state(id: str, state: str|bool)

Update the state of a light. off|false = off, on|true = on

## lights.async_update_value(id: str, value: int)

Update the brightness of a light, and assumes 0 is off.

## things.async_update_value(id: str, value : int|bool)

Update the value of a thing. 0|false = off, 100|true = on

## \*.async_update(data: dict)

Directly update with data to the endpoint.

# Example

```{.python}
import asyncio
import aiohttp
from advantage_air import advantage_air


async def main():
    async with aiohttp.ClientSession() as session:
        aa = advantage_air("192.168.1.24", port=2025, session=session, retry=5)
        if data := await aa.async_get(1):
            print(data)
            aa.aircon.async_update_ac("ac1",{"state": "on"})
            await asyncio.gather(
                aa.aircon.async_update_zone("ac1","z01", {"value": 25}),
                aa.aircon.async_update_zone("ac1","z02", {"value": 50}),
            )

asyncio.run(main())
```
