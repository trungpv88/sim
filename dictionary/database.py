__author__ = 'User'
import pickle
import os
DB_PATH = "db.pkl"


class DataBase(object):
    """
    Words are saved in database under dictionary type.
    The keys are words and the values are their definitions under list type.
    For example:
    {'hello':['1. def1', '2. def2'], 'world':['1. w1', '2. w2']}
    """
    def __init__(self):
        self.name = None

    @staticmethod
    def save(obj=dict()):
        """
        Save data under dictionary type to database
        :param obj:
        :return:
        """
        with open(DB_PATH, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        """
        Load words from database under dictionary type
        :return:
        """
        if not os.path.exists(DB_PATH):
            self.save()
        with open(DB_PATH, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def normalize_saved_def(lines):
        """
        Normalize word definitions taken from html source page.
        It's saved under a list so that each item shows a definition of word.
        :param lines:
        :return:
        """
        lines = lines.split('\n')
        normal_lines = []
        line_num = 1
        for line in lines:
            if line is not '':
                normal_line = line.replace(':', '.')  # replace last character from ':' to '.'
                # upper first character and insert space at the beginning of line
                if normal_line[0] is not ' ':
                    normal_line = ' ' + normal_line[0].upper() + normal_line[1:]
                else:
                    normal_line = normal_line[0] + normal_line[1].upper() + normal_line[2:]
                # insert definition number at beginning of line
                normal_line = str(line_num) + '.' + normal_line
                normal_lines.append(normal_line)
                line_num += 1
        return normal_lines
