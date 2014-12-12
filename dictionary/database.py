import pickle
import os
DB_PATH = "db.pkl"
LOG_PATH = 'log.pkl'
IMAGE_PATH = 'image.pkl'


class BaseModel(object):
    """
    A abstract class to access database
    """
    def __init__(self, path):
        self.path = path

    def save(self, obj=dict()):
        """
        Save data under dictionary type to database
        :param obj:
        :return:
        """
        with open(self.path, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        """
        Load data from database under dictionary type
        :return:
        """
        if not os.path.exists(self.path):
            self.save()
        with open(self.path, 'rb') as f:
            return pickle.load(f)


class DataBase(BaseModel):
    """
    Words are saved in database under dictionary type.
    The keys are words and the values are their definitions under list type.
    For example:
    {'hello':['1. def1', '2. def2'], 'world':['1. w1', '2. w2']}
    """
    def __init__(self):
        super(DataBase, self).__init__(DB_PATH)
        self.name = None

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


class LogDB(BaseModel):
    """
    Log database contains some information like: the learned day, ..
    """
    def __init__(self):
        super(LogDB, self).__init__(LOG_PATH)


class ImageDB(BaseModel):
    """
    Image database contains the description images
    """
    def __init__(self):
        super(ImageDB, self).__init__(IMAGE_PATH)

