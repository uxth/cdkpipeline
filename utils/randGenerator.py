import string
import random


def stringGenerator(length: int):
    letters = string.ascii_letters + string.digits + string.punctuation
    res = random.choice(string.ascii_letters)
    res = res.join(random.choice(string.digits))
    res = res.join(random.choice(string.punctuation))
    res = res.join(random.choice(letters) for i in range(length - 3))
    # print(res)
    return res
