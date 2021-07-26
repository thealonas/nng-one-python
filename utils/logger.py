# -*- coding: utf-8 -*-
import os
import colorful as cf
from framework.raw_saves import NNGRawSaves
from framework.globals import Globals


class Logger:
    class level:
        none = 0
        success = 1
        warn = 2
        error = 3
        tagged_success = 4
        debug = 5
        hell = 10

    class config_logging_level:
        log_nothing = 0
        log_errors = 1
        log_debug = 2
        log_hell = 10

    @staticmethod
    def clear():
        if os.name != "nt":
            os.system("clear")
        else:
            os.system("cls")

    @staticmethod
    def log(msg: str, tp: int = 1, name: str = "NNG One", force: bool = False):
        self = Logger
        try:
            debug = NNGRawSaves().debug
        except Exception:
            debug = self.level.none
        if tp == self.level.success:
            print(cf.bold_green(f"[{name}] {msg}"))
        elif tp == self.level.warn:
            print(cf.bold_blue(f"[{name}] {msg}"))
        elif tp == self.level.tagged_success:
            print(cf.bold_green(f"[{name}] {Globals.tag} | {msg}"))
        elif (
            tp == self.level.error and debug >= self.config_logging_level.log_errors
        ) or force:
            print(cf.bold_red(f"[{name}] [ERROR] {msg}"))
        elif (
            tp == self.level.debug and debug >= self.config_logging_level.log_debug
        ) or force:
            print(cf.bold_purple(f"[{name}] [DEBUG] {msg}"))
        elif tp == self.level.hell and debug >= self.config_logging_level.log_hell:
            print(cf.bold_grey(f"{name} [HELL] {msg}"))
