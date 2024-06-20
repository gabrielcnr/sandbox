import functools
import queue
import threading

q = queue.Queue()

def process_background_tasks_loop():
    while True:
        func, args, kwargs = q.get()
        func(*args, **kwargs)


background_task_thread = threading.Thread(target=process_background_tasks_loop, daemon=True)
background_task_thread.start()


def run_in_background(func, *args, **kwargs):
    q.put((func, args, kwargs))


def background_task(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        run_in_background(func, *args, **kwargs)
    return wrapper