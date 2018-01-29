# -*- coding: utf-8 -*-
"""Proof-of-work system algorithm. Required to validate transactions

https://en.wikipedia.org/wiki/Proof-of-work_system
https://en.wikipedia.org/wiki/Hashcash
"""
import random
import hashlib
import time
import base64
import uuid
from datetime import datetime


def get_hash(val):
    return hashlib.sha1(str(val).encode()).hexdigest()


def b64(val):
    return base64.b64encode(str(val).encode()).decode()


def verify_header(val: str) -> bool:
    return get_hash(val).startswith(5 * '0')


def x_hash_cash_header(resource: str) -> str:
    """Calculate X-Hashcash header

    Format:
    ver:bits:date-YYMMDD[hhmm[ss]]:resource:ext(ignored):rand:counter

    :param resource: resource identifier, e.g email
    """

    dt = datetime.utcnow().strftime('%Y%M%d%H%M%S')
    rand = b64(uuid.uuid4())
    cnt = random.randint(1, 2**20)

    h = '1:20:{dt}:{resource}::{rand}:{counter}'.format(
        dt=dt, resource=resource, rand=rand, counter=b64(cnt))

    while not verify_header(h):
        cnt += 1
        h = '1:20:{dt}:{resource}::{rand}:{counter}'.format(
            dt=dt, resource=resource, rand=rand, counter=b64(cnt))
    return h


if __name__ == '__main__':
    t0 = time.time()
    header = x_hash_cash_header('test@gmail.com')

    print(header)
    print('Elapsed: {}s'.format(time.time() - t0))
