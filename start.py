# -*- coding: utf-8 -*-
from framework.saves import NNGSaves
from logger import Logger as lg
from utils import utils
from utils.sentry import Sentry


def check_for_data():
    sv = NNGSaves().load()
    try:
        sv["com"]
        sv["sentry"]
        lists = sv["lists"]
        lists["banlist"]
        lists["grouplist"]
        lists["loadtype"]
    except (KeyError, TypeError):
        lg.log("NNG One", "Данные повреждены", 3)
        NNGSaves().dialog(first=True)


if __name__ == "__main__":
    saves = NNGSaves()
    check_for_data()
    while True:
        sentry = Sentry()
        if saves.load()["sentry"]:
            client = sentry.init()
            with client:
                utils.NNGUtils().main(sentry=True)
        else:
            utils.NNGUtils().main(sentry=False)
