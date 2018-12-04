import time
from threading import Thread

def loop(f, retry):
    while True: 
        f()
        time.sleep(retry)

def retry_decorator(retry=1):
    def retry_decorator_func(f):
        def loop_decorator(*args, **kwargs):
            th = Thread(target = loop, args = (f, retry))
            th.start()
        return loop_decorator
    return retry_decorator_func




# loop(sandor,2)
# sandor("sii")
# sandor("noo")