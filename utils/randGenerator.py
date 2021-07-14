import string
import random


def stringGenerator(length: int):
    res = ''
    while len(res) < length:
        if len(res) < length:
            res += random.choice(string.ascii_letters)
        if len(res) < length:
            res += random.choice(string.digits)
        if len(res) < length:
            res += random.choice(string.punctuation)
    print(res)
    return res
