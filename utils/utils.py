# -*- coding: utf-8 -*-
import traceback
from typing import Union
from sentry_sdk import capture_exception
from framework.core import NNGCore
from framework.functions import Category
from framework.functions import Function
from framework.saves import NNGSaves
from logger import Logger as lg
from other.exceptions import ReturnBack
from other.cmd_helper import CMDHelper


class NNGUtils:
    framework = None
    name = "NNG One"
    helper = CMDHelper()

    @staticmethod
    def init():
        # Категории
        categories = [
            Category(1, "Блокировка"),
            Category(2, "Разблокировка"),
            Category(3, "Редакторы"),
            Category(4, "Поиск"),
            Category(5, "Прочее"),
        ]
        # Функции
        functions = [
            [Function(1, 1, "Пользователя"), Function(1, 2, "Пользователей")],
            [Function(2, 1, "Пользователя"), Function(2, 2, "Пользователей")],
            [Function(3, 1, "Выдача"), Function(3, 2, "Снятие")],
            [Function(4, 1, "Заблокированных редакторов"), Function(4, 2, "Редактора")],
            [
                Function(5, 1, "Репост записи в сообщества"),
                Function(5, 2, "Преобразование sceen_name в ID"),
                Function(5, 3, "Удаление всех записей со стены"),
                Function(5, 4, "Статистика"),
                Function(5, 5, "Настройки"),
            ],
        ]

        return categories, functions

    def get_choose(
        self, promt: str, maxValue: int, rng: list[int], is_category_choose: bool = True
    ):
        lg.log(self.name, "Выберете пункт меню:\n\n", 1)
        print(promt) if is_category_choose else print(
            f"{promt}{maxValue + 1}. Вернуться назад\n\n"
        )
        choose = str(input(">"))
        # Учитываем вернуться назад как пункт меню, он всегда на один больше максимального значения
        rng[1] += 1

        if not choose.isdigit():
            lg.clear()
            lg.log(self.name, "Неверный пункт меню!", 2)
            return self.get_choose(promt, maxValue, rng, is_category_choose)
        choose = int(choose)
        if maxValue + 1 == choose:
            return False
        if 0 < choose <= maxValue:
            return choose
        lg.clear()
        lg.log(self.name, "Неверный пункт меню!", 2)
        return self.get_choose(promt, maxValue, rng, is_category_choose)

    @staticmethod
    def wait_for_reply():
        input("Для продолжения нажмите ENTER...\n")

    def menu(self, messages: list[dict[str, int]], category: int = None) -> Function:
        lg.clear()
        for msg in messages:
            try:
                msg["message"]
                msg["type"]
            except (TypeError, KeyError):
                continue
            lg.log(self.name, msg["message"], msg["type"])
        cats, funcs = self.init()
        category_txt = function_txt = str()
        functions = str()
        for cat in cats:
            category_txt += f"{cat.cid}. {cat.name}\n\n"
        choose = (
            category
            if category is not None
            else self.get_choose(
                category_txt, rng=[1, cats[-1].cid], maxValue=cats[-1].cid
            )
        )
        if not choose:
            self.menu(messages)
        try:
            functions = funcs[choose - 1]
        except IndexError:
            lg().log("NNG One", "Число не может быть равным или меньше нуля", 3)
            lg.clear()
            self.menu(messages)
        exitValue = -1
        for func in functions:
            function_txt += f"{func.fid}. {func.name}\n\n"
            if exitValue < func.fid:
                exitValue = func.fid
        exitValue += 1
        lg.clear()
        choose = self.get_choose(
            function_txt,
            rng=[1, functions[-1].fid],
            maxValue=functions[-1].fid,
            is_category_choose=False,
        )
        if choose:
            function = functions[choose - 1]
            return function
        function = self.menu(messages)
        return function

    def main(self, sentry: bool = True, function: Function = None):
        saves = NNGSaves()
        token = saves.load()
        lg.clear()
        while type(token) is not dict:
            lg.log(self.name, "Данные о токене повреждены", 3)
            saves.dialog(first=True)
            self.main()
        token = token["token"]
        core = NNGCore(token)
        if not core.is_authorized():
            lg.log(self.name, "Данные о токене повреждены", 3)
            saves.token_upd()
            self.main()
        messages = [
            {
                "message": "Отчёты об ошибках отключены. К сожалению мы не сможем их справить в случае возникновения",
                "type": 2,
            }
            if not sentry
            else None,
            {"message": core.msg, "type": 1},
        ]
        try:
            cid = function.cid if function is not None else None
            function = self.menu(messages=messages, category=cid)
            if function.cid == 1:
                core.block(function)
            elif function.cid == 2:
                core.unblock(function)
            elif function.cid == 3:
                core.manager(function)
            elif function.cid == 4:
                core.community(function)
            elif function.cid == 5:
                core.other(function)
        except ReturnBack as back:
            lg.clear()
            self.main(function=back.function)
        except (ValueError, KeyError) as e:
            lg.log(self.name, f"Произошла ошибка: {e}", 3)
            lg.log(self.name, "Похоже, что данные в конфиге некорректны", 2)
            if self.helper.get_yn_choose("Хотите ли заполнить конфиг повторно?"):
                saves.dialog(first=True)
        except Exception as e:
            string = traceback.format_exc()
            load = saves.load()
            event = capture_exception(e) if load["sentry"] else str()
            message = f"Ваш event_id: {event}" if load["sentry"] else str()
            lg.log(
                "NNG One",
                f"Упс! Похоже Вы нашли баг. Отправьте нам его в гитхаб, приложив текст ниже{' и Ваш event_id.' if load['sentry'] else '.'}\n{message}",
                3,
            )
            print(string)
            self.wait_for_reply()
