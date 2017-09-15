#!/usr/bin/env python
# encoding: utf-8

import random

class Random(object):
    def __init__(self):
        self.CHAR_SET = [
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
            "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
            "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        ]
        self.NUM_SET = [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ]
        self.char_len = len(self.CHAR_SET)
        self.num_len = len(self.NUM_SET)

    def rand_str(self, len):
        str = ""
        for i in range(len):
            str += self.CHAR_SET[random.randint(0, self.char_len-1)]

        return str

    def rand_num(self, len):
        str = ""
        for i in range(len):
            str += self.NUM_SET[random.randint(0, self.num_len-1)]

        return str

    def rand_int(self, a, b):
        return random.randint(a, b)

