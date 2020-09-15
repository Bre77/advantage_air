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
        self.ready = True
        self.queue = {}

    async def async_get(self):
        data = {}
        count = 0
        while count < self.retry:
            try:
                async with request(
                    "GET", f"http://{self.ip}:{self.port}/getSystemData", timeout=ClientTimeout(total=4)
                ) as resp:
                    assert resp.status == 200
                    data = await resp.json(content_type=None)
            except ConnectionResetError:
                pass
            except ServerConnectionError:
                pass

            if "aircons" in data:
                return data

            count += 1
            await asyncio.sleep(1)
        raise Exception(f"Connection failed {MYAIR_RETRY} times")

    async def async_change(self, change):
        self.queue = update(self.queue, change)
        if self.ready:
            self.ready = False
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
                    self.ready = True
                    raise Exception(data["reason"])
            self.ready = True
        return len(self.queue)

    async def queue(self,change):
        self.queue = update(self.queue, change)
        return