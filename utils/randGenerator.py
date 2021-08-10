import string
import random


def stringGenerator(length: int):
    res = random.choice(string.ascii_lowercase)
    res += random.choice(string.ascii_uppercase)
    res += random.choice(string.digits)
    res += random.choice(string.punctuation)
    while len(res) < length:
        choice = random.randint(0, 3)
        if choice == 0:
            res += random.choice(string.ascii_letters)
        elif choice == 1:
            res += random.choice(string.digits)
        else:
            res += random.choice(string.punctuation)
    # print(res)
    return res
