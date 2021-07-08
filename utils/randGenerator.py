import string
import random


def stringGenerator(length: int):
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for i in range(length - 3)).join(random.choice(string.ascii_letters)).join(
        random.choice(string.digits)).join(random.choice(string.punctuation))
