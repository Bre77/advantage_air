import json
import asyncio
import aiohttp
import collections.abc
from datetime import timedelta


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class ApiError(Exception):
    """AdvantageAir Error"""

    def __init__(self, message):
        super().__init__(message)


class advantage_air:
    """AdvantageAir Connection"""

    def __init__(self, ip, port=2025, session=None, retry=5):

        self.ip = ip
        self.port = port
        self.session = session
        self.retry = retry
        self.changes = {}
        self.lock = asyncio.Lock()
        if session is None:
            session = aiohttp.ClientSession()
        self.data = {}

    async def async_get(self, retry=None):
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
                        self.data = data

                        #MyAir5 fix
                        if data["system"]["sysType"] == "MyAir5":
                            for ac in data:
                                try:
                                    if data[ac]["info"]["fan"] == "autoAA":
                                        data[ac]["info"]["fan"] = "auto"
                                except KeyError:
                                    pass

                        return data
            except (aiohttp.ClientError, aiohttp.ClientConnectorError, aiohttp.client_exceptions.ServerDisconnectedError, ConnectionResetError) as err:
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

    async def async_change(self, change):
        """Merge changes with queue and send when possible, returning True when done"""
        
        #MyAir5 fix
        if self.data and self.data["system"]["sysType"] == "MyAir5":
            for ac in change:
                try:
                    if change[ac]["info"]["fan"] == "auto":
                        change[ac]["info"]["fan"] = "autoAA"
                except KeyError:
                    pass

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
                        f"http://{self.ip}:{self.port}/setAircon",
                        params={"json": json.dumps(payload)},
                        timeout=aiohttp.ClientTimeout(total=4),
                    ) as resp:
                        data = await resp.json(content_type=None)
                    if data["ack"] == False:
                        raise ApiError(data["reason"])
                except (aiohttp.client_exceptions.ServerDisconnectedError, ConnectionResetError) as err:
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
