from pynput.keyboard import Listener
import queue
import json
import asyncio
import websockets
import argparse


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


def motor_command(left_speed, left_direction, right_speed, right_direction):
    return {
        'left_speed': left_speed,
        'left_direction': left_direction,
        'right_speed': right_speed,
        'right_direction': right_direction,
    }


async def direction_forwarder(q, server, port):
    websocket = await websockets.connect(f"ws://{server}:{port}/")
    consumer_task = asyncio.ensure_future(robot_recv(websocket))
    producer_task = asyncio.ensure_future(robot_send(websocket, q))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()


async def robot_recv(websocket):
    async for message in websocket:
        print(message)


async def robot_send(websocket, q):
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

        if go_left and go_forward:
            motors = motor_command(0.6, 0, 0.4, 0)
        elif go_right and go_forward:
            motors = motor_command(0.4, 0, 0.6, 0)
        elif go_left and go_backward:
            motors = motor_command(0.6, 1, 0.4, 1)
        elif go_right and go_backward:
            motors = motor_command(0.4, 1, 0.6, 1)
        elif go_forward:
            motors = motor_command(0.5, 0, 0.5, 0)
        elif go_backward:
            motors = motor_command(0.5, 1, 0.5, 1)
        elif go_left:
            motors = motor_command(0.5, 0, 0.5, 1)
        elif go_right:
            motors = motor_command(0.5, 1, 0.5, 0)
        else:
            motors = motor_command(0, 1, 0, 1)

        await websocket.send(json.dumps({'data': {'motors': motors}}))

parser = argparse.ArgumentParser(prog='robot-client')
parser.add_argument('--server', dest='server', default='127.0.0.1')
parser.add_argument('--port', dest='port', default='1974')
args = parser.parse_args()

# Collect events until released, on windows the key listener runs in operating system thread
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    asyncio.ensure_future(consume_keys(sync_raw_q, async_raw_q))
    asyncio.ensure_future(key_repeat_filter(async_raw_q, unique_q))
    asyncio.get_event_loop().run_until_complete(direction_forwarder(unique_q, args.server, args.port))

