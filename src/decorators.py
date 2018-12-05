import time
from threading import Thread


def loop(f, retry, args, kwargs):
    while True:
        f(*args, **kwargs)
        time.sleep(retry)


def retry_decorator(retry=1):
    def retry_decorator_func(f):
        def loop_decorator(*args, **kwargs):
            th = Thread(target=loop, args=(f, retry, args, kwargs))
            th.start()

        return loop_decorator

    return retry_decorator_func

# loop(sandor,2)
# sandor("sii")
# sandor("noo")
