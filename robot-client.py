from pynput.keyboard import Key, Listener
import queue
import threading
import json
import asyncio
import websockets

raw_q = queue.Queue()
uniq_q = queue.Queue()


# queue key events
def on_press(key):
    raw_q.put('{0} pressed'.format(key))


def on_release(key):
    raw_q.put('{0} release'.format(key))


async consume_keys(from, to):
    while True:
        item = await asyncio.get_event_loop().run_in_executor()
        await

class KeyRepeatFilter(object):
    prev = None

    def __init__(self, from, to):
        self.q = q

    def __call__(self):
        if self.prev != item:
            self.prev = item
            self.q.put(item)


class DirectionForwarder(object):
    right = False
    left = False
    forward = False
    backward = False

    def __call__(self, item):
        key, action = item.split()
        on = True if action == "pressed" else False

        if key == "Key.right":
            self.right = on
        elif key == "Key.left":
            self.left = on
        elif key == "Key.up":
            self.forward = on
        elif key == "Key.down":
            self.backward = on

        go_left = self.left and not self.right
        go_right = self.right and not self.left
        go_forward = self.forward and not self.backward
        go_backward = self.backward and not self.forward

        turn = ""
        direction = ""

        if go_left: turn = "left"
        if go_right: turn = "right"
        if go_forward: direction = "forward"
        if go_backward: direction = "backward"


        print(json.dumps({'turn': turn, 'direction': direction}))


def make_worker(q, callable):
    def worker():
        while True:
            item = q.get()
            if item is None:
                break
            callable(item)
            q.task_done()
    return worker


def make_thread(q, callable):
    worker_thread = threading.Thread(target=make_worker(q, callable))
    worker_thread.start()
    threads.append(worker_thread)


threads = []
make_thread(raw_q, KeyRepeatFilter(uniq_q))
make_thread(uniq_q, DirectionForwarder())

# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
