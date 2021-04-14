# -*- coding: utf-8 -*-
import os
import colorful as cf


class Logger:
    @staticmethod
    def clear():
        if os.name != "nt":
            os.system("clear")
        else:
            os.system("cls")

    @staticmethod
    def log(name: str, msg: str, tp: int = 1):
        """
        0 - typical
        1 - success
        2 - warn
        3 - error
        """
        if tp == 0:
            print(cf.bold(f"[{name}] {msg}"))
        elif tp == 1:
            print(cf.bold_green(f"[{name}] {msg}"))
        elif tp == 2:
            print(cf.bold_blue(f"[{name}] {msg}"))
        elif tp == 3:
            print(cf.bold_red(f"[{name}] {msg}"))
