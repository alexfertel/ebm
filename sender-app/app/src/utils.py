#!/usr/bin/env python3.6
from .config import *


def cut(body: str, size: int = MESSAGE_LENGTH) -> list:
    length = len(body)
    if size > length:
        val = ''
        result = []
        for i in range(length):
            if i % size == 0:
                result.append(val)
                val = ''
            else:
                val += body[i] if i != length else body[i]
        return result
    else:
        return [body]


def inbetween(a, b, c):
    """
    Is c between a and b
    :param a: int
    :param b: int
    :param c: int
    :return: bool
    """
    a = a % SIZE
    b = b % SIZE
    c = c % SIZE
    if a < b:
        return a <= c <= b
    return a <= c or c <= b


def in_queue(id: str, queue: list):
    for item_id, item in queue:
        if id == item_id:
            return item
    return None
