import time
import config

from threading import Thread


def loop(f, sleep_time, args, kwargs):
    while True:
        f(*args, **kwargs)
        time.sleep(sleep_time)


def retry(sleep_time=1):
    def decorator(f):
        def wrapper(*args, **kwargs):
            th = Thread(target=loop, args=(f, sleep_time, args, kwargs))
            th.start()

        return wrapper

    return decorator


def retry_times(times):
    def decorator(f):
        def wrapper(*args, **kwargs):
            count = 0
            while count < times:
                try:
                    ret = f(*args, **kwargs)
                    return ret
                except:
                    time.sleep(config.RETRY_ON_FAILURE_DELAY)
                    count += 1

        return wrapper

    return decorator
