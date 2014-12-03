#!/usr/bin/env python

"""
Learning english application
"""

from word.word import Word
from dictionary.database import DataBase

if __name__ == "__main__":
    print __doc__
    word = "hi"
    dict_db = DataBase()
    tmp = dict_db.load()
    w1 = Word(value=word)
    if word not in tmp.keys():
        tmp[word] = w1.get_definition()
    dict_db.save(tmp)
    # w1.show_definition()
    w1.get_pronunciation()
    w1.pronounce()
    tmp2 = dict_db.load()
    print tmp2[word]