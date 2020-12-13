#!/usr/bin/env python3

PERIOD = 5
RFC3339 = '%Y-%m-%dT%H:%M:%SZ'

import sys
import json
import time
import asyncio

# https://websockets.readthedocs.io/
import websockets

class RISliveWebsocket():

    def __init__(self, router, asn):
        self.router = router
        self.asn = asn

    async def __aenter__(self):
        self._conn = await websockets.connect("wss://ris-live.ripe.net/v1/ws/?client=asynchronous-python-script-by-me")
        opening = json.dumps({"type": "ris_subscribe", "data": {"host": self.router, "path": self.asn}})
        await self._conn.send(opening)
        print("Connected, %s sent" % opening, file=sys.stderr)
        return self

    async def __aexit__(self, *args, **kwargs):
        print("Goodbye", file=sys.stderr)
        pass

    async def send(self, message):
        await self._conn.send(message)

    async def receive(self):
        return await self._conn.recv()

async def tick():
    while True:
        await asyncio.sleep(PERIOD)
        print("Waking up, it is %s" % time.strftime(RFC3339, time.gmtime(time.time())), file=sys.stderr)

async def main(router, asn):
    sock = RISliveWebsocket(router, asn)
    async with sock as feed:
        while True:
            x = await feed.receive()
            message = json.loads(x)
            bgp_message = message['data']
            if bgp_message['type'] == 'UPDATE':
                if 'withdrawals' in bgp_message:
                    continue
                if 'announcements' in bgp_message:
                    for net in bgp_message['announcements']:
                        for networks in net['prefixes']:
                            print (networks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([main('rrc21', None), tick()]))
