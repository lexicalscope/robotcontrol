from pynput.keyboard import Listener
import queue
import json
import asyncio
import websockets


sync_raw_q = queue.Queue()
async_raw_q = asyncio.Queue()
unique_q = asyncio.Queue()


# queue key events
def on_press(key):
    sync_raw_q.put('{0} pressed'.format(key))


def on_release(key):
    sync_raw_q.put('{0} release'.format(key))


async def consume_keys(from_q, to_async_q):
    while True:
        item = await asyncio.get_event_loop().run_in_executor(None, queue.Queue.get, from_q)
        await to_async_q.put(item)


async def key_repeat_filter(from_q, to_q):
    prev = None

    while True:
        item = await from_q.get()
        if prev != item:
            prev = item
            await to_q.put(item)


async def direction_forwarder(q ):
    websocket = await websockets.connect('ws://localhost:8765/')

    right = False
    left = False
    forward = False
    backward = False

    while True:
        item = await q.get()
        key, action = item.split()
        on = True if action == "pressed" else False

        if key == "Key.right":
            right = on
        elif key == "Key.left":
            left = on
        elif key == "Key.up":
            forward = on
        elif key == "Key.down":
            backward = on

        go_left = left and not right
        go_right = right and not left
        go_forward = forward and not backward
        go_backward = backward and not forward

        turn = ""
        direction = ""

        if go_left:
            turn = "left"
        if go_right:
            turn = "right"
        if go_forward:
            direction = "forward"
        if go_backward:
            direction = "backward"

        message = json.dumps({'turn': turn, 'direction': direction})
        await websocket.send(message)


# Collect events until released, on windows the key listener runs in operating system thread
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    asyncio.ensure_future(consume_keys(sync_raw_q, async_raw_q))
    asyncio.ensure_future(key_repeat_filter(async_raw_q, unique_q))
    asyncio.ensure_future(direction_forwarder(unique_q))

