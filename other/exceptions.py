# -*- coding: utf-8 -*-
from logger import Logger as lg


class MissingData(Exception):
    pass


class ReturnBack(Exception):
    def __init__(self, function=None):
        lg.clear()
        self.function = function or None
