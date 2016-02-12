#!/usr/bin/env python3

from functools import reduce
import os

DATA_FIXTURES = [
    'demo_data.json',
    ]

ARGS = reduce(lambda s1,s2 : s1 + ' ' + s2,DATA_FIXTURES)
COMMAND = 'python manage.py loaddata '+ARGS
print(COMMAND)
os.system(COMMAND)
