import json
import asyncio
import collections.abc
from datetime import timedelta
from aiohttp import request, ClientError, ClientTimeout, ServerConnectionError


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class advantage_air:
    """AdvantageAir Connection"""

    def __init__(self, ip, port=2025, retry=5):
        self.ip = ip
        self.port = port
        self.retry = retry
        self.queue = {}
        self.lock = asyncio.Lock()

    async def async_get(self, retry=None):
        retry = retry or self.retry
        data = {}
        count = 0
        while count < retry:
            count += 1
            try:
                async with request(
                    "GET", f"http://{self.ip}:{self.port}/getSystemData", timeout=ClientTimeout(total=4)
                ) as resp:
                    assert resp.status == 200
                    data = await resp.json(content_type=None)
            except (ClientError, asyncio.TimeoutError):
                pass
            except SyntaxError:
                break

            if "aircons" in data:
                return data
            
            await asyncio.sleep(1)
        raise ClientError(f"No valid response after {count} failed attempt{['','s'][count>1]}")

    async def async_change(self, change):
        self.queue = update(self.queue, change)
        if not self.lock.locked():
            async with self.lock:
                while self.queue:
                    payload = self.queue
                    self.queue = {}
                    async with request(
                        "GET",
                        f"http://{self.ip}:{self.port}/setAircon",
                        params={"json": json.dumps(payload)},
                        timeout=ClientTimeout(total=4),
                    ) as resp:
                        data = await resp.json(content_type=None)
                    if data["ack"] == False:
                        raise Exception(data["reason"])
        return len(self.queue)

    async def queue(self,change):
        self.queue = update(self.queue, change)
        return