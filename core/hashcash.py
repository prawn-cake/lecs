# -*- coding: utf-8 -*-
"""Proof-of-work system algorithm to achieve a distributed consensus in this
case
https://en.wikipedia.org/wiki/Proof-of-work_system
"""
import random
import hashlib
import time


def get_hash(s):
    return hashlib.sha1(str(s).encode()).hexdigest()


def verify_header(sha1):
    return sha1.startswith(5 * '0')


if __name__ == '__main__':
    t0 = time.time()
    r = random.randint(1, 2**160)
    cur_hash = get_hash(r)
    while not verify_header(cur_hash):
        r += 1
        cur_hash = get_hash(r)

    print(cur_hash)
    print('Elapsed: {}s'.format(time.time() - t0))
