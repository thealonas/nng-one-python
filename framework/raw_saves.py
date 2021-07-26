# -*- coding: utf-8 -*-
import json


class NNGRawSaves:
    """
    Необходимо, чтобы не было цирковых импортов у логгера с сохранениями.
    """

    @property
    def debug(self) -> int:
        with open("config.json", encoding="utf8") as f:
            return json.load(f)["debug"]
