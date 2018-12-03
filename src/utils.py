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
