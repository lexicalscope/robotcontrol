import asyncio
import websockets
import json


async def robot(websocket, path):
    async for message in websocket:
        command = json.loads(message)

        # forward sets both motors to half speed
        print("rr.set_motors(0.5, 0, 0.5, 0)")

        # backward sets both motors to half speed
        print("rr.set_motors(0.5, 1, 0.5, 1)")

        # left sets left motor in reverse, right motor in forward
        print("rr.set_motors(0.5, 0, 0.5, 1)")

        # right sets right motor in reverse, left motor in forward
        print("rr.set_motors(0.5, 1, 0.5, 0)")

        print(message)

asyncio.ensure_future(websockets.serve(robot, port=8765))
asyncio.get_event_loop().run_forever()

