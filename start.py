# -*- coding: utf-8 -*-
from utils import utils
from utils.sentry import Sentry
from framework.saves import NNGSaves


if __name__ == "__main__":
    saves = NNGSaves()
    while True:
        if not saves.check_for_config():
            saves.dialog(True)
        sentry = Sentry()
        if saves.sentry:
            client = sentry.init()
            with client:
                utils.NNGUtils().main()
        else:
            utils.NNGUtils().main()
