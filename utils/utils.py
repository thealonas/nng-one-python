# -*- coding: utf-8 -*-
import typing
import traceback
from sentry_sdk import capture_exception
from framework.core import NNGCore
from framework.functions import Category
from framework.functions import Function
from framework.saves import NNGSaves
from framework.update import NNGUpdate
from utils.logger import Logger as lg
from other.cmd_helper import CMDHelper
from other.exceptions import ReturnBack


class NNGUtils:
    name = "NNG One"
    helper = CMDHelper()

    def __init__(self):
        self.saves = NNGSaves()
        self.update = NNGUpdate()
        self.core = NNGCore(self.saves.token)
        self.messages = [
            {
                "message": "Отчёты об ошибках отключены. К сожалению мы не сможем их исправить в случае возникновения",
                "type": 2,
            }
            if not self.saves.sentry
            else None,
            {"message": self.core.msg, "type": 4},
            {
                "message": f"Ваша версия ({self.update.version}) устарела. "
                f"Требуется обновление до {self.update.new_version}",
                "type": 2,
            }
            if self.update.if_update_need()
            else {
                "message": "Текущая версия NNG One не нуждается в обновлении",
                "type": 1,
            },
        ]
        self.core.set_messages(self.messages)
        lg.clear()

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

    def menu(self, category: int = None) -> Function:
        lg.clear()

        def get_string_value_for_functions(
            funcs: typing.List[Function],
        ) -> str:

            int_value = -1
            txt = str()

            # Цикл определяет номер функции для выхода из меню и текст
            for func in funcs:
                txt += f"{func.fid}. {func.name}\n\n"
                if int_value < func.fid:
                    int_value = func.fid

            return txt

        def get_string_value_for_categories(categories: typing.List[Category]) -> str:
            txt = str()

            # Цикл определяет текст
            for func_category in categories:
                txt += f"{func_category.cid}. {func_category.name}\n\n"

            return txt

        def get_category_list_range(
            element: typing.List[Category],
        ) -> typing.List[int]:
            return [1, element[-1].cid]

        menu_categories, menu_functions = self.init()

        # Работа с категориями

        category_txt = get_string_value_for_categories(menu_categories)

        rng = get_category_list_range(menu_categories)

        choose = category or self.helper.get_title_choose(
            category_txt,
            rng=rng,
            maxValue=menu_categories[-1].cid,
            messages=self.messages,
            do_not_show_exit=True,
        )

        if not choose:
            return self.menu()

        # Работа с функциями

        try:
            functions = menu_functions[choose - 1]
        except IndexError:
            lg.log("Число не может быть равным или меньше нуля", lg.level.warn)
            return self.menu()

        function_txt = get_string_value_for_functions(functions)
        lg.clear()

        choose = self.helper.get_title_choose(
            function_txt,
            maxValue=functions[-1].fid,
            rng=[1, functions[-1].fid],
            do_not_show_exit=False,
            messages=self.messages,
        )

        if choose:
            function = functions[choose - 1]
            return function

        function = self.menu()
        return function

    def main(self, function: Function = None):
        saves = self.saves
        self.core = NNGCore(saves.token)
        core = self.core
        self.messages = [
            {
                "message": "Отчёты об ошибках отключены. К сожалению мы не сможем их исправить в случае возникновения",
                "type": lg.level.warn,
            }
            if not self.saves.sentry
            else None,
            {"message": self.core.msg, "type": lg.level.tagged_success},
            {
                "message": f"Ваша версия ({self.update.version}) устарела. "
                f"Требуется обновление до {self.update.new_version}",
                "type": lg.level.warn,
            }
            if self.update.if_update_need()
            else None,
        ]
        self.core.set_messages(self.messages)
        lg.clear()
        if not core.is_authorized():
            lg.log("Необходимо обновить токен", lg.level.error, self.name, force=True)
            saves.update_token()
            self.main()
        try:
            cid = function.cid if function is not None else None
            function = self.menu(category=cid)
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
        except (
            FileNotFoundError,
            OSError,
            saves.Exceptions.BadData,
            saves.Exceptions.BadUrl,
        ) as e:
            if e is not None and len(str(e)) > 0:
                lg.log(f"Произошла ошибка: {e}", lg.level.debug, self.name)
            lg.log(
                "Похоже, что данные в конфиге некорректны",
                lg.level.warn,
                self.name,
                force=True,
            )
            if self.helper.get_yn_choose("Хотите ли Вы заполнить конфиг повторно?"):
                saves.dialog(first=True)
        except Exception as e:
            string = traceback.format_exc()
            event = capture_exception(e) if saves.sentry else str()
            message = f"Ваш event_id: {event}" if saves.sentry else str()
            lg.log(
                f"Упс! Похоже Вы нашли баг. Отправьте нам его в гитхаб, "
                f"приложив текст ниже{' и Ваш event_id' if saves.sentry else ''}\n{message}",
                lg.level.error,
                force=True,
            )
            print(string)
            self.helper.idle()
