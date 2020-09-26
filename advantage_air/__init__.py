import json
import asyncio
import collections.abc
from datetime import timedelta
from aiohttp import request, ClientError, ClientTimeout


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class ApiError(Exception):
    """AdvantageAir Error"""

    def __init__(self,message):
        super().__init__(message)


class advantage_air:
    """AdvantageAir Connection"""

    def __init__(self, ip, port=2025, retry=5):
        self.ip = ip
        self.port = port
        self.retry = retry
        self.changes = {}
        self.lock = asyncio.Lock()

    async def async_get(self, retry=None):
        retry = retry or self.retry
        data = {}
        count = 0
        error = None
        while count < retry:
            count += 1
            try:
                async with request(
                    "GET", f"http://{self.ip}:{self.port}/getSystemData", timeout=ClientTimeout(total=4)
                ) as resp:
                    assert resp.status == 200
                    data = await resp.json(content_type=None)
                    if "aircons" in data:
                        return data
            except ClientError as err:
                error = err
                pass
            except asyncio.TimeoutError as err:
                error = "Connection timed out."
                pass
            except SyntaxError as err:
                error = err
                break

            await asyncio.sleep(1)
        raise ApiError(f"No valid response after {count} failed attempt{['','s'][count>1]}. Last error was: {error}")

    async def async_change(self, change):
        """Merge changes with queue and send when possible, returning True when done"""
        self.changes = update(self.changes, change)
        if self.lock.locked():
            return False
        async with self.lock:
            while self.changes:
                payload = self.changes
                self.changes = {}
                async with request(
                    "GET",
                    f"http://{self.ip}:{self.port}/setAircon",
                    params={"json": json.dumps(payload)},
                    timeout=ClientTimeout(total=4),
                ) as resp:
                    data = await resp.json(content_type=None)
                if data["ack"] == False:
                    raise Exception(data["reason"])
        return True

