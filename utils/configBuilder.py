import json

from dictor import dictor


class Config:
    def __init__(self, path: str):
        with open(path) as f:
            self.data = json.load(f)

    def getValue(self, path: str):
        res = dictor(self.data, path)
        if not res:
            raise Exception('No value found for ' + path)
        return res
