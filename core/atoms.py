# -*- coding: utf-8 -*-
"""Different core pieces. This file will be split into several ones"""

import collections.abc


class Block(object):
    """Block primitive. Should be immutable and contain set of transactions
    as a Merkle-tree"""
    pass


class Blockchain(collections.abc.Sequence):
    """Immutable blockchain data structure.
    To add a new item into a blockchain you need to clone it and pass new item
    as a parameter

    >>> blockchain = Blockchain.empty()
    >>> blockchain = blockchain.clone('new_block')
    >>> assert len(blockchain) == 1
    """

    def __init__(self, data):
        self._data = data

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def clone(self, new_item):
        return Blockchain([*self._data, new_item])

    @staticmethod
    def empty():
        return Blockchain(data=[])


class Client(object):
    def __init__(self):
        self.block_chain = Blockchain.empty()


if __name__ == '__main__':
    pass
