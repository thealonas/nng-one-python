# -*- coding: utf-8 -*-
import json
import webbrowser
import colorful as cf
from other.cmd_helper import CMDHelper
from other.exceptions import ReturnBack
from framework.functions import Function
from logger import Logger as lg


class NNGSaves:
    name = "NNG Saves"
    tokenurl = "https://oauth.vk.com/authorize?client_id=7436182&scope=270340&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1"
    helper = CMDHelper()

    def dialog(self, first: bool = None, function: Function = None):
        lg.clear()
        if first:
            print(
                f'{cf.bold_green("[NNG Saves] [Main] Приветсвуем в разделе сохранения и загрузки настроек NNG Utils")}'
            )
            choose = 1
        else:
            lg.log(
                self.name,
                cf.bold_green(
                    "[Main] Приветсвуем в разделе сохранения и загрузки настроек NNG Utils"
                ),
            )
            choose = self.helper.get_choose(
                "1. Редактировать настройки\n\n2. Обновить токен\n\n3. Редактировать отчеты об ошибках\n\n4. Вернуться назад",
                4,
            )
        if choose == 4:
            raise ReturnBack if function is None else ReturnBack(function)
        if choose == 1:
            token = self.helper.get_string_choose(
                'Введите токен (получить можно, введя в это поле "token"): '
            )
            while token == "token":
                webbrowser.open(self.tokenurl)
                token = self.helper.get_string_choose("Введите токен: ")
            sentry = True
            if not first:
                sentry = self.helper.get_yn_choose(
                    cf.bold_blue("Включить автоматическую отправку отчетов об ошибке?")
                )
            banlist = grouplist = "None"
            loadtype = self.helper.get_string_choose(
                "Введите тип загрузок списков (0 — из URL, 1 — из файлов): "
            )
            while loadtype not in ["1", "0"]:
                loadtype = self.helper.get_string_choose(
                    "Введите тип загрузок списков (0 — из URL, 1 — из файлов): "
                )
            if loadtype == "0":
                banlist = self.helper.get_string_choose(
                    "Введите URL на список заблокированных: "
                )
                grouplist = self.helper.get_string_choose(
                    "Введите URL на список сообществ: "
                )
            elif loadtype == "1":
                banlist = self.helper.get_string_choose(
                    "Введите локальный URL на список заблокированных: "
                )
                grouplist = self.helper.get_string_choose(
                    "Введите локальный URL на список сообществ: "
                )
            com = self.helper.get_string_choose("Введите комментарий для блокировки: ")
            data = {
                "token": token,
                "com": com,
                "sentry": sentry,
                "lists": {
                    "loadtype": loadtype,
                    "banlist": banlist,
                    "grouplist": grouplist,
                },
            }
            self.save(data)
        elif choose == 2:
            self.token_upd()
        elif choose == 3:
            self.sentry_upd()
        elif choose == 4:
            raise ReturnBack if function is None else ReturnBack(function)
        else:
            return

    @staticmethod
    def save(data: dict):
        try:
            with open("config.json", "w") as f:
                json.dump(data, f, sort_keys=True, indent=4)
        except Exception as error:
            lg.log("NNG Saves", f"Выявлено исключение при сохранении данных: {error}")
            return False
        else:
            return True

    def token_upd(self):
        data = self.load()
        token = self.helper.get_string_choose(
            'Введите токен (получить можно, введя в это поле "token"): '
        )
        while token == "token":
            webbrowser.open(self.tokenurl)
            token = self.helper.get_string_choose("Введите токен: ")
        data["token"] = token
        self.save(data)
        print("\n[NNG Saves Debug] Успешно!")

    def is_key_exists(self, key) -> bool:
        """
        :param key: Key for check
        :return: Bool
        """
        data = self.load()
        try:
            data[key]
            return True
        except KeyError:
            return False

    def sentry_upd(self):
        data = self.load()
        data["sentry"] = self.helper.get_yn_choose(
            cf.bold_blue("Включить автоматическую отправку отчетов об ошибке?")
        )
        self.save(data)
        lg.log(self.name, "Успешно!")

    def load(self, ex: bool = None):
        try:
            with open("config.json") as f:
                if ex:
                    data = self.load()
                    try:
                        return json.load(f)
                    except Exception:
                        self.save(data)
                else:
                    return json.load(f)
        except Exception as error:
            lg.log("NNG Saves", f"Выявлено исключение при распаковке данных: {error}")
            return False
