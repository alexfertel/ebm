import config
import time
import logging
import pickle

from threading import Thread

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('DECORATOR')

thread_count = 0


def loop(f, sleep_time, args, kwargs):
    while True:
        time.sleep(sleep_time)
        f(*args, **kwargs)


def retry(sleep_time=1):
    def decorator(f):
        def wrapper(*args, **kwargs):
            global thread_count
            th = Thread(target=loop, args=(f, sleep_time, args, kwargs))
            thread_count += 1
            logger.info(f'\nStarted thread with retry loop for function: {f.__name__}.')
            logger.info(f'Thread Count: {thread_count}.\n')
            th.daemon = True
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

            logger.error(f'Exceeded retry_times when calling: {f.__name__}({args}, {kwargs}).')
            return None

        return wrapper

    return decorator


def thread(f):
    def thread_decorator(*args, **kwargs):
        global thread_count
        th = Thread(target=f, args=args, kwargs=kwargs)
        thread_count += 1
        th.daemon = True
        th.start()

    return thread_decorator


def required_auth(context):
    def auth_function(f):
        def auth_decorator(*args, **kwargs):
            user_active = pickle.loads(context.exposed_get(int(kwargs['token'])))
            if user_active is not None:
                f(args, kwargs)

        return auth_decorator

    return auth_function
