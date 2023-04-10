import json
import asyncio
import aiohttp
import collections.abc

ON = "ON"
OFF = "OFF"

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class ApiError(Exception):
    """AdvantageAir Error"""


class advantage_air:
    """AdvantageAir Connection"""

    def __init__(self, ip: str, port: int=2025, session: aiohttp.ClientSession=None, retry: int=5):
        if session is None:
            session = aiohttp.ClientSession()

        self.ip = ip
        self.port = port
        self.session = session
        self.retry = retry

        self.aircon = self._aircon(ip, port, session, retry)
        self.lights = self._lights(ip, port, session, retry)
        self.things = self._things(ip, port, session, retry)

    async def async_get(self, retry:int =None):
        retry = retry or self.retry
        data = {}
        count = 0
        error = None
        while count < retry:
            count += 1
            try:
                async with self.session.get(
                    f"http://{self.ip}:{self.port}/getSystemData",
                    timeout=aiohttp.ClientTimeout(total=4),
                ) as resp:
                    assert resp.status == 200
                    data = await resp.json(content_type=None)
                    if "aircons" in data:
                        return data
            except (
                aiohttp.ClientError,
                aiohttp.ClientConnectorError,
                aiohttp.client_exceptions.ServerDisconnectedError,
                ConnectionResetError,
            ) as err:
                error = err
            except asyncio.TimeoutError:
                error = "Connection timed out."
            except AssertionError:
                error = "Response status not 200."
                break
            except SyntaxError as err:
                error = "Invalid response"
                break

            await asyncio.sleep(1)
        raise ApiError(
            f"No valid response after {count} failed attempt{['','s'][count>1]}. Last error was: {error}"
        )

    class _endpoint:
        def __init__(self, ip, port, session, retry) -> None:
            self.ip = ip
            self.port = port
            self.session = session
            self.retry = retry
            self.changes = {}
            self.lock = asyncio.Lock()

        async def async_update(self, change: dict[str, any]) -> bool:
            """Merge changes with queue and send when possible, returning True when done"""

            self.changes = update(self.changes, change)
            if self.lock.locked():
                return False
            async with self.lock:
                while self.changes:
                    # Allow any addition changes from the event loop to be collected
                    await asyncio.sleep(0)
                    # Collect all changes
                    payload = self.changes
                    self.changes = {}
                    try:
                        async with self.session.get(
                            f"http://{self.ip}:{self.port}/{self.endpoint}",
                            params={"json": json.dumps(payload)},
                            timeout=aiohttp.ClientTimeout(total=4),
                        ) as resp:
                            data = await resp.json(content_type=None)
                        if data["ack"] == False:
                            raise ApiError(data["reason"])
                    except (
                        aiohttp.client_exceptions.ServerDisconnectedError,
                        ConnectionResetError,
                    ) as err:
                        # Recoverable error, reinsert the changes and try again in a second
                        self.changes = update(self.changes, payload)
                        await asyncio.sleep(1)
                    except aiohttp.ClientError as err:
                        raise ApiError(err)
                    except asyncio.TimeoutError:
                        raise ApiError("Connection timed out.")
                    except AssertionError:
                        raise ApiError("Response status not 200.")
                    except SyntaxError as err:
                        raise ApiError("Invalid response")
            return True

    class _aircon(_endpoint):
        """Aircon endpoint"""

        endpoint = "setAircon"

        async def async_update_ac(self, ac: str, body: dict) -> bool:
            """Update an aircon"""
            return await self.async_update({ac: {"info": body}})

        async def async_update_zone(self, ac: str, zone: str, body: dict) -> bool:
            """Update a zone"""
            return await self.async_update({ac: {"zones": {zone: body}}})

    class _lights(_endpoint):
        """Lights endpoint"""

        endpoint = "setLights"

        async def async_update_state(self, id: str, state: str|bool) -> bool:
            """Update a lights state"""
            if state == True:
                state = ON
            elif state == False:
                state = OFF
            return await self.async_update({id: {"id": id, "state": state}})

        async def async_update_value(self, id: str, value: int) -> bool:
            """Update a lights state and value"""
            return await self.async_update({id: {"id": id, "state": (ON if value > 0 else OFF), "value": value}})

    class _things(_endpoint):
        """Things endpoint"""

        endpoint = "setThings"

        async def async_update_value(self, id: str, value: int|bool) -> bool:
            """Update a things state and value"""
            if value == True:
                value = 100
            elif value == False:
                value = 0
                
            return await self.async_update({id: {"id": id, "value": value}})
