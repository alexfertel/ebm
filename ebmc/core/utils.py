#!/usr/bin/env python3.6
import hashlib
from core import config


def cut(l: str, n: int = config.MESSAGE_LENGTH):
    result = []
    for i in range(0, len(l), n):
        result.append(l[i:i + n])
    return result


def in_queue(id: str, queue: list):
    for item_id, item in queue:
        if id == item_id:
            return item
    return None


def inbetween(a, b, c):
    """
    Is c between a and b
    :param a: int
    :param b: int
    :param c: int
    :return: bool
    """
    a = a % config.SIZE
    b = b % config.SIZE
    c = c % config.SIZE
    if a < b:
        return a <= c <= b
    return a <= c or c <= b


def hashing(obj):
    return int(hashlib.sha1(str(obj).encode()).hexdigest(), 16)
