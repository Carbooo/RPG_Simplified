#!/usr/bin/env python

import asyncio
#import datetime
import random
import websockets

@asyncio.coroutine
def handler(websocket, path):
    while True:
        message = yield from websocket.recv()
        yield from websocket.send(message)
        yield from asyncio.sleep(random.random() * 3)

start_server = websockets.serve(handler, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()