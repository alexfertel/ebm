import time
from threading import Thread


def loop(f, sleep_time, args, kwargs):
    while True:
        f(*args, **kwargs)
        time.sleep(sleep_time)


def retry(sleep_time=1):
    def retry_decorator_func(f):
        def loop_decorator(*args, **kwargs):
            th = Thread(target=loop, args=(f, sleep_time, args, kwargs))
            th.start()

        return loop_decorator

    return retry_decorator_func

# loop(sandor,2)
# sandor("sii")
# sandor("noo")
