# -*- coding: utf-8 -*-
from other.cmd_helper import CMDHelper as cmd
from other.exceptions import ReturnBack
from utils.logger import Logger as lg


class Function:
    cid = fid = int()
    name = str()

    def __init__(self, cid: int, fid: int, name: str):
        """
        :param cid: ID категории
        :param fid: ID функции
        :param name: ID категории
        """

        self.cid = cid
        self.fid = fid
        self.name = name


class Category:
    cid = int()
    name = str()

    def __init__(self, cid: int, name: str):
        """
        :param cid: ID категории
        :param name: Имя категории
        """

        self.cid = cid
        self.name = name


# Для core.py
def operation(function):
    def wrapper(*args):
        lg.clear()
        function(*args)
        lg.log("Операция завершена", tp=lg.level.warn, force=True)
        cmd.idle()
        raise ReturnBack

    return wrapper


# Для сейвов
def clear(function):
    def wrapper(*args):
        lg.clear()
        function(*args)
        lg.clear()

    return wrapper
