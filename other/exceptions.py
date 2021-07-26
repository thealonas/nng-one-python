# -*- coding: utf-8 -*-
from utils.logger import Logger as lg


class ReturnBack(Exception):
    def __init__(self, function=None):
        super(ReturnBack, self).__init__()
        lg.clear()
        self.function = function or None
