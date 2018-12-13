#!/usr/bin/env python3.6
from .config import *


def cut(l: str, n: int = MESSAGE_LENGTH):
    result = []
    for i in range(0, len(l), n):
        result.append(l[i:i + n])
    return result


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
    print(f"\nQueue {queue}\n")
    for item in queue:
        if id == item.subject['message_id']:
            return item
    return None
