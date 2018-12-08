#!/usr/bin/env python3.6
import rpyc
import fire
import pickle


def main(ip, port):
    c = rpyc.connect(ip, port).root

    print(c.identifier())
    print(c.get_successors())
    print(c.finger_table())

    print(c.get(101010))

    print(pickle.loads(c.get_data()))
    print(pickle.loads(c.get_all()))


if __name__ == '__main__':
    fire.Fire(main)
