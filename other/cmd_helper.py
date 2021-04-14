# -*- coding: utf-8 -*-
from typing import Union
from logger import Logger as lg


class CMDHelper:
    def get_choose(self, promt: str, maxValue: int) -> Union[int, bool]:
        lg.log("NNG One", "Выберете пункт меню:\n\n", 1)
        print(f"{promt}\n\n")
        choose = str(input(">"))
        if not choose.isdigit():
            lg.clear()
            lg.log("NNG One", "Неверный пункт меню!", 2)
            return self.get_choose(promt, maxValue)
        choose = int(choose)
        if 0 < choose <= maxValue:
            return choose
        lg.clear()
        lg.log("NNG One", "Неверный пункт меню!", 2)
        return self.get_choose(promt, maxValue)

    def get_string_choose(self, promt: str, minlen: int = 1) -> str:
        lg.log("NNG One", promt, 1)
        variable = str(input(">"))
        if len(variable) < minlen:
            lg.log("NNG One", "Введенная переменная слишком короткая!", 3)
            return self.get_string_choose(promt, minlen)
        return variable

    @staticmethod
    def get_yn_choose(promt: str) -> bool:
        choose = str(input(f"{promt} (Y - Да, N - Нет): "))
        choose = choose.lower()
        while choose not in ["y", "n"]:
            choose = str(input("Y - Да, N - Нет: "))
            choose = choose.lower()
        return choose == "y"
