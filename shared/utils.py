from ..config import *


def cut(body: str, max_length: int = message_length) -> list:
    length = len(body)
    if max_length > length:
        val = ''
        result = []
        for i in range(length):
            if i % max_length == 0:
                result.push(val)
                val = ''
            else:
                val += body[i] if i != length else body[i]
        return result

    else:
        return [body]
