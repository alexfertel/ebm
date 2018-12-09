#!/usr/bin/env python3.6
import rpyc
import fire
import pickle


def main(ip, port):
    c = rpyc.connect(ip, port).root

    print('identifier()')
    print(c.identifier())
    print('get_successors()')
    print(c.get_successors())
    print(c.finger_table())

    # print('Get 101010')
    # print(c.get(101010))
    # 
    # print('Get 101010')
    # c.set(101010, pickle.dumps('papelito'))
    # c.set(101010, pickle.dumps('papelote'))
    # c.set(2**15, pickle.dumps('pizarra'))
    # c.set(2**16, pickle.dumps('pizarra'))
    # 
    # print('Get 101010')
    # print(pickle.loads(c.get(101010)))
    # 
    # print('Get 101010')
    # c.set(1, pickle.dumps('1'))
    # c.set(2**80, pickle.dumps('2**80'))
    # c.set(2**58, pickle.dumps('2**58'))
    # c.set(2**120, pickle.dumps('2**120'))
    # 
    # # print('Get 101010')
    # # print(pickle.loads(c.get(101010)))
    # 
    # print('Get 101010')
    # c.set(2**159, pickle.dumps('2**159'))
    # c.set(2**39, pickle.dumps('2**39'))
    # c.set(2**135, pickle.dumps('2**135'))
    # c.set(2**100, pickle.dumps('2**100'))
    # 
    # # print('Get 101010')
    # # print(pickle.loads(c.get(101010)))

    print(f'pickle.loads(c.get_owner({101010}))')
    print(c.get_owner(101010))
    print('pickle.loads(c.get_data())')
    print(pickle.loads(c.get_data()))
    print('pickle.loads(c.get_replicas())')
    print(pickle.loads(c.get_replicas()))
    print('pickle.loads(c.get_all())')
    print(pickle.loads(c.get_all()))


if __name__ == '__main__':
    fire.Fire(main)
