# -*- coding: utf-8 -*-
import re
import requests
from utils.logger import Logger as lg
from framework.globals import Globals


class NNGUpdate:
    name = "NNG Update"
    api_url = "https://api.github.com/repos/likhner/nng-one/releases/latest"

    def __init__(self):
        self.version = Globals.tag

    @property
    def github_data(self) -> dict:
        return requests.get(self.api_url).json()

    def if_update_need(self) -> bool:
        github_data = self.github_data
        try:
            # Регулярные выражения удаляют всё, кроме цифр. Так можно сравнивать версии через операторы.
            new = int(re.sub(r"\D", r"", github_data[r"tag_name"]))
            current = int(re.sub(r"\D", r"", self.version))
            if new > current:
                return True
        except KeyError:
            lg.log(
                "Не удалось соеденится с серверами GitHub для проверки обновлений",
                lg.level.error,
            )
        return False

    @property
    def new_version(self) -> str:
        return self.github_data["tag_name"]
