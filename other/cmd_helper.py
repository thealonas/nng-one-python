# -*- coding: utf-8 -*-
import typing
import colorful as cf
from utils.logger import Logger as lg
from utils.url_checker import is_valid_url


class CMDHelper:
    def get_title_choose(
        self,
        show_string: str,
        maxValue: int,
        rng: typing.List[int],
        do_not_show_exit: bool = False,
        messages: list[dict] = None,
    ):
        if messages is not None:
            self.message_handler(messages)
        lg.log("Выберете пункт меню:\n\n", 1)
        print(
            f"{show_string}{maxValue + 1}. Вернуться назад\n\n"
            if not do_not_show_exit
            else f"{show_string}"
        )
        choose = str(input(">"))

        # Учитываем вернуться назад как пункт меню, он всегда на один больше максимального значения
        rng[1] += 1
        if not choose.isdigit():
            lg.clear()
            lg.log("Неверный пункт меню!", 2)
            return self.get_title_choose(
                show_string, maxValue, rng, do_not_show_exit, messages
            )
        choose = int(choose)
        if maxValue + 1 == choose:
            return False
        if 0 < choose <= maxValue:
            return choose
        lg.clear()
        lg.log("Неверный пункт меню!", 2)
        return self.get_title_choose(
            show_string, maxValue, rng, do_not_show_exit, messages
        )

    def get_menu_choose(
        self,
        show_string: str,
        maxValue: int,
        is_category: bool = False,
        messages: typing.List[dict] = None,
        title_string: str = None,
    ):
        if messages is not None:
            self.message_handler(messages)
        if title_string is not None:
            lg.log(title_string, tp=lg.level.success)
        lg.log("Выберете пункт меню:\n\n", 1)
        print(
            f"{show_string}{maxValue + 1}. Вернуться назад\n\n"
            if is_category
            else f"{show_string}\n\n"
        )
        choose = str(input(">"))
        if not choose.isdigit():
            lg.clear()
            lg.log("Неверный пункт меню!", 2)
            return self.get_menu_choose(
                show_string, maxValue, is_category, messages, title_string
            )
        choose = int(choose)
        if 0 < choose <= maxValue:
            return choose
        lg.clear()
        lg.log("Неверный пункт меню!", 2)
        return self.get_menu_choose(
            show_string, maxValue, is_category, messages, title_string
        )

    @staticmethod
    def get_string_choose(show_string: str, minimal_length: int = 1) -> str:
        lg.log(show_string, lg.level.success)
        variable = str(input(">"))
        while len(variable) < minimal_length:
            lg.log("Вы ввели слишком короткое значение", lg.level.warn, force=True)
            variable = str(input(">"))
        return variable

    @staticmethod
    def get_url_choose(show_string: str) -> str:
        lg.log(show_string, lg.level.success)
        url = str(input(">"))
        while not is_valid_url(url):
            lg.log("Введите правильный URL!", lg.level.warn, force=True)
            url = str(input(">"))
        return url

    def get_int_choose(
        self,
        show_string: str,
        maxValue: int,
        minValue: int = 1,
        custom_error: str = None,
    ):
        value = str(input(cf.bold_green(f"{show_string}: ")))
        if not value.isdigit():
            lg.log(custom_error or "Введёная строка — не число", lg.level.warn)
            return self.get_int_choose(
                show_string, maxValue, minValue=minValue, custom_error=custom_error
            )
        if maxValue < int(value):
            lg.log(custom_error or f"Максимум этого числа — {maxValue}", lg.level.warn)
            return self.get_int_choose(
                show_string, maxValue, minValue=minValue, custom_error=custom_error
            )
        if int(value) < minValue:
            lg.log(custom_error or f"Минимум этого числа — {minValue}", lg.level.warn)
            return self.get_int_choose(
                show_string, maxValue, minValue=minValue, custom_error=custom_error
            )
        return int(value)

    @staticmethod
    def message_handler(messages: typing.List[dict]):
        for message in messages:
            if message is None or not message:
                continue
            lg.log(message["message"], message["type"])

    @staticmethod
    def get_yn_choose(show_string: str) -> bool:
        choose = str(input(cf.bold_blue(f"{show_string} (Y - Да, N - Нет): ")))
        while choose.lower() not in ["y", "n"]:
            choose = str(input("Y - Да, N - Нет: "))
        return choose.lower() == "y"

    @staticmethod
    def idle():
        input(cf.bold_blue("\nНажмите Enter для продолжения…"))
