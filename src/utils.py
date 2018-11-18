from ..config import *


def cut(body: str, size: int = message_length) -> list:
    length = len(body)
    if size > length:
        val = ''
        result = []
        for i in range(length):
            if i % size == 0:
                result.push(val)
                val = ''
            else:
                val += body[i] if i != length else body[i]
        return result

    else:
        return [body]
