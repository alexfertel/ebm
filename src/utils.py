import config


def cut(body: str, size: int = config.MESSAGE_LENGTH) -> list:
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
    a = a % config.SIZE
    b = b % config.SIZE
    c = c % config.SIZE
    if a < b:
        return a <= c <= b
    return a <= c or c <= b
