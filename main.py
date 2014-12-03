#!/usr/bin/env python

"""
Learning english application
"""

from word.word import Word
from dictionary.database import DataBase

if __name__ == "__main__":
    print __doc__
    word = "how"
    dict_db = DataBase()
    tmp = dict_db.load()
    w1 = Word(value=word)
    if word not in tmp.keys():
        word_def = w1.get_definition()
        if word_def is not "":
            tmp[word] = word_def
    dict_db.save(tmp)
    # w1.show_definition()
    w1.get_pronunciation()
    w1.pronounce()
    tmp2 = dict_db.load()
    print tmp2[word]