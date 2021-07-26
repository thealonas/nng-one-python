# -*- coding: utf-8 -*-
import json
import webbrowser
import colorful as cf
from framework.functions import Function
from framework.functions import clear
from other.cmd_helper import CMDHelper
from other.exceptions import ReturnBack
from utils.logger import Logger as lg
from utils.url_checker import is_valid_url


class NNGSaves:
    name = "NNG Saves"
    token_url = "https://oauth.vk.com/authorize?client_id=7436182&scope=270340&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1"
    helper = CMDHelper()
    function = None
    msg = "Приветствуем в разделе сохранения и загрузки настроек NNG One"

    class Exceptions:
        class BadData(Exception):
            pass

        class WrongSaveType(Exception):
            pass

        class BadUrl(Exception):
            pass

    def dialog(self, first: bool = None, function: Function = None):
        self.function = function
        while True:
            lg.clear()
            if first:
                choose = -1
            else:
                choose = self.helper.get_menu_choose(
                    "1. Токен\n\n2. Списки\n\n3. Комментарий при блокировке\n\n"
                    "4. Отправка отчётов об ошибках\n\n5. Состояние Callback\n\n6. Обход капчи\n\n"
                    "7. Откладка\n\n8. Вернуться назад",
                    8,
                    title_string=self.msg,
                )
            if choose == 8:
                raise ReturnBack if function is None else ReturnBack(function)

            if choose == -1:
                self.dialog_default()
                break

            if choose == 1:
                self.update_token()

            elif choose == 2:
                self.update_lists()

            elif choose == 3:
                self.update_com()

            elif choose == 4:
                self.update_sentry()

            elif choose == 5:
                self.update_callback()

            elif choose == 6:
                self.update_captcha()

            elif choose == 7:
                self.update_debug()

    @staticmethod
    def __save(data: dict):
        try:
            with open("config.json", "w") as f:
                json.dump(data, f, sort_keys=True, indent=4)
        except Exception as error:
            lg.log(
                f"Выявлено исключение при сохранении данных: {error}", name="NNG Saves"
            )
            return False
        else:
            return True

    def save_default(
        self, token: str, com: str, load: int, ban_list: str, group_list: str
    ):
        data = {
            "token": token,
            "com": com,
            "sentry": True,
            "switch_callback": True,
            "captcha": {"ban": False, "editor": True},
            "debug": lg.config_logging_level.log_nothing,
            "lists": {
                "load_type": load,
                "ban_list": ban_list,
                "group_list": group_list,
            },
        }
        self.__save(data)

    def dialog_default(self):
        token = self.helper.get_string_choose(
            'Введите токен (получить можно, введя в это поле "token"): '
        )
        while token == "token":
            webbrowser.open(self.token_url)
            token = self.helper.get_string_choose("Введите токен: ")
        ban_list = group_list = "None"
        load_type = self.helper.get_int_choose(
            show_string="Выберите тип загрузок списков (0 — из URL, 1 — из файлов)",
            maxValue=1,
            minValue=0,
            custom_error="Выберите между загрузкой из URL (0) или загрузкой из файлов (1)",
        )
        if load_type == 0:
            ban_list = self.helper.get_url_choose(
                "Введите URL на список заблокированных: "
            )
            group_list = self.helper.get_url_choose("Введите URL на список сообществ: ")
        elif load_type == 1:
            ban_list = self.helper.get_string_choose(
                "Введите локальный URL на список заблокированных: "
            )
            group_list = self.helper.get_string_choose(
                "Введите локальный URL на список сообществ: "
            )
        com = self.helper.get_string_choose(
            "Введите комментарий при блокировки (можно оставить пустым): ",
            minimal_length=0,
        )
        self.save_default(token, com, load_type, ban_list, group_list)

    def check_for_config(self) -> bool:
        try:
            check = (
                type(self.captcha_ban) is bool
                and type(self.captcha_editor) is bool
                and type(self.comment) is str
                and type(self.debug) is int
                and type(self.ban_list) is str
                and type(self.group_list) is str
                and type(self.load_type) is int
                and type(self.sentry) is bool
                and type(self.callback) is bool
                and type(self.token) is str
            )
            if not check:
                raise self.Exceptions.WrongSaveType
            if (
                self.load_type == 0
                and not is_valid_url(self.ban_list)
                and not is_valid_url(self.group_list)
            ):
                return False
            return True
        except (
            self.Exceptions.BadData,
            self.Exceptions.WrongSaveType,
            self.Exceptions.BadUrl,
        ):
            return False

    @property
    def captcha_ban(self) -> bool:
        return self.__load()["captcha"]["ban"]

    @captcha_ban.setter
    def captcha_ban(self, value: bool):
        data = self.__load()
        data["captcha"]["ban"] = value
        self.__save(data)

    @property
    def captcha_editor(self) -> bool:
        return self.__load()["captcha"]["editor"]

    @captcha_editor.setter
    def captcha_editor(self, value: bool):
        data = self.__load()
        data["captcha"]["editor"] = value
        self.__save(data)

    @property
    def comment(self) -> str:
        return self.__load()["com"]

    @comment.setter
    def comment(self, value: str):
        data = self.__load()
        data["com"] = value
        self.__save(data)

    @property
    def debug(self) -> int:
        return self.__load()["debug"]

    @debug.setter
    def debug(self, value: int):
        data = self.__load()
        data["debug"] = value
        self.__save(data)

    @property
    def ban_list(self) -> str:
        return self.__load()["lists"]["ban_list"]

    @ban_list.setter
    def ban_list(self, value: str):
        data = self.__load()
        data["lists"]["ban_list"] = value
        self.__save(data)

    @property
    def group_list(self) -> str:
        return self.__load()["lists"]["group_list"]

    @group_list.setter
    def group_list(self, value: str):
        data = self.__load()
        data["lists"]["group_list"] = value
        self.__save(data)

    @property
    def load_type(self) -> int:
        return self.__load()["lists"]["load_type"]

    @load_type.setter
    def load_type(self, value: int):
        data = self.__load()
        data["lists"]["load_type"] = value
        self.__save(data)

    @property
    def sentry(self) -> bool:
        return self.__load()["sentry"]

    @sentry.setter
    def sentry(self, value: bool):
        data = self.__load()
        data["sentry"] = value
        self.__save(data)

    @property
    def callback(self) -> bool:
        return self.__load()["switch_callback"]

    @callback.setter
    def callback(self, value: bool):
        data = self.__load()
        data["switch_callback"] = value
        self.__save(data)

    @property
    def token(self) -> str:
        return self.__load()["token"]

    @token.setter
    def token(self, value: str):
        data = self.__load()
        data["token"] = value
        self.__save(data)

    def update_captcha(self):
        captcha_ban = self.helper.get_yn_choose("Обходить каптчу при блокировках?")
        captcha_editor = self.helper.get_yn_choose(
            "Обходить каптчу при выдаче редактора?"
        )
        self.captcha_ban = not captcha_ban
        self.captcha_editor = not captcha_editor

    def update_token(self):
        token = self.helper.get_string_choose(
            'Введите токен (получить можно, введя в это поле "token"): '
        )
        while token == "token":
            webbrowser.open(self.token_url)
            token = self.helper.get_string_choose("Введите токен: ")
        self.token = token

    @clear
    def update_lists(self):
        choose = self.helper.get_menu_choose(
            "1. Тип списков\n\n2. URL на список заблокированных\n\n3. URL на список групп\n\n4. Вернуться назад",
            4,
        )
        if choose == 4:
            self.dialog(function=self.function)
        elif choose == 1:
            self.load_type = self.helper.get_int_choose(
                show_string="Выберите тип загрузок списков (0 — из URL, 1 — из файлов)",
                maxValue=1,
                minValue=0,
                custom_error="Выберите между загрузкой из URL (0) или загрузкой из файлов (1)",
            )
        elif choose == 2:
            if self.load_type == 0:
                self.ban_list = self.helper.get_url_choose(
                    "Введите URL на список заблокированных"
                )
            elif self.load_type == 1:
                self.ban_list = self.helper.get_string_choose(
                    "Введите локальный URL на список заблокированных"
                )
        elif choose == 3:
            if self.load_type == 0:
                self.ban_list = self.group_list = self.helper.get_url_choose(
                    "Введите URL на список сообществ: "
                )
            elif self.load_type == 1:
                self.ban_list = self.group_list = self.helper.get_string_choose(
                    "Введите локальный URL на список сообществ: "
                )

    @clear
    def update_debug(self):
        choose = self.helper.get_menu_choose(
            "1. Показывать только ошибки\n\n2. Показывать всё\n\n3. Отключить откладку\n\n4. Вернуться назад",
            4,
        )
        if choose == 4:
            self.dialog(function=self.function)
        elif choose == 1:
            self.debug = lg.config_logging_level.log_errors
        elif choose == 2:
            self.debug = lg.config_logging_level.log_debug
        elif choose == 3:
            self.debug = lg.config_logging_level.log_nothing

    def update_callback(self):
        self.callback = self.helper.get_yn_choose(
            "Отключать Callback у сообществ при массовых действиях?"
        )

    def update_sentry(self):
        self.sentry = self.helper.get_yn_choose(
            cf.bold_blue("Включить автоматическую отправку отчетов об ошибке?")
        )

    def update_com(self):
        self.comment = self.helper.get_string_choose(
            "Введите комментарий при блокировки (можно оставить пустым): ",
            minimal_length=0,
        )

    def __load(self):
        try:
            with open("config.json") as f:
                return json.load(f)
        except Exception as error:
            raise self.Exceptions.BadData(
                f"Ошибка при распаковке: {error} | Тип: {type(error)}"
            )
