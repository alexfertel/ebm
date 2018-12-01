import hashlib
from config import MAX_BITS


class Finger:
    def __init__(self, start: int = -1, interval: tuple = tuple(), node: int = -1):
        self.start = start
        self.interval = interval
        self.node = node


class Node:
    def __init__(self, identifier):
        self.__id = int(hashlib.sha1(str(identifier).encode()).hexdigest(), 16)
        # Compute Finger Table computable properties (start, interval).
        # The .node property is computed when a node joins or leaves and at the chord start
        self.ft = {
            i: Finger(start=(self.identifier + 2 ** (i - 1)) % 2 ** MAX_BITS)
            for i in range(1, MAX_BITS + 1)
        }

        for i in range(1, len(self.ft)):
            finger.interval = self.ft[i].start, self.ft[i + 1].start

        self.ft[0] = 'unknown'  # At first the predecessor is unknown

    @property
    def identifier(self):
        return self.__id

    @property
    def successor(self) -> int:
        return self.ft[1].node

    @property
    def predecessor(self) -> int:
        return self.ft[0].node

    def find_successor(self, identifier) -> Node:
        n_prime = self.find_predecessor(identifier)
        return n_prime.successor

    # FIXME: Hay que anhadir los rpc y hay que migrar este codigo al server
    def find_predecessor(self, identifier) -> Node:
        n_prime: Node = self
        # compute closest finger preceding id
        while not (n_prime.identifier < identifier <= n_prime.successor):
            for i in range(len(n_prime.ft) - 1, 0, -1):
                if self.ft[i].interval[0] + 1 < identifier <= n_prime.ft[i].interval[1] + 1:
                    n_prime = self.ft[i].node
        return n_prime

    def get(self, key):
        pass

    def set(self, key, value):
        pass
