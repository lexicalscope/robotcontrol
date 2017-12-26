import asyncio
import websockets
import json
import argparse
from rrb3 import RRB3


rr = RRB3(1.2*6, 6) # battery voltage, motor voltage

parser = argparse.ArgumentParser(prog='robot-server')
parser.add_argument('--bind', dest='bind', default='')
parser.add_argument('--port', dest='port', default='1974')
args = parser.parse_args()


async def robot(websocket, path):
    consumer_task = asyncio.ensure_future(robot_recv(websocket))
    producer_task = asyncio.ensure_future(robot_send(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()


async def robot_send(websocket):
    while True:
        await asyncio.sleep(0.1)
        distance = rr.get_distance()
        await websocket.send(json.dumps({'data': {'distance': distance}}))


async def robot_recv(websocket):
    async for message in websocket:
        command = json.loads(message)

        motors = command['data']['motors']
        rr.set_motors(
                motors['left_speed'], 
                motors['left_direction'], 
                motors['right_speed'], 
                motors['right_direction'])

asyncio.ensure_future(websockets.serve(robot, host=args.bind, port=args.port))
asyncio.get_event_loop().run_forever()

