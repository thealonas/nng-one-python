# -*- coding: utf-8 -*-
from other.exceptions import ReturnBack
from logger import Logger as lg


class Function:
    cid = fid = int()
    name = str()
    function = None

    def __init__(self, cid: int, fid: int, name: str):
        """
        :param cid: ID of category
        :param fid: Function ID
        :param name: Function name
        """

        self.cid = cid
        self.fid = fid
        self.name = name


class Category:
    cid = int()
    name = str()

    def __init__(self, cid: int, name: str):
        """
        :param cid: ID of category
        :param name: Category name
        """

        self.cid = cid
        self.name = name


def operation(function):
    def wrapper(*args):
        lg.clear()
        function(*args)
        input("Нажмите Enter для продолжения...\n")
        raise ReturnBack

    return wrapper
