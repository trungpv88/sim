__author__ = 'User'
import pickle
import os
DB_PATH = "db.pkl"


class DataBase(object):
    def __init__(self):
        self.name = None

    def save(self, obj=dict()):
        with open(DB_PATH, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        if not os.path.exists(DB_PATH):
            self.save()
        with open(DB_PATH, 'rb') as f:
            return pickle.load(f)
