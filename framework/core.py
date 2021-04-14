# -*- coding: utf-8 -*-
import urllib.request
import colorful as cf
from framework.api import NNGFramework
from framework.functions import Function
from framework.functions import operation
from framework.saves import NNGSaves
from logger import Logger as lg
from other.cmd_helper import CMDHelper
from other.exceptions import ReturnBack


class NNGCore:
    name = msg = "NNG Core"
    helper = CMDHelper()

    def __init__(self, token):
        lg().clear()
        self.framework = NNGFramework(token)
        self.msg = self.framework.get_auth_msg()

    def is_authorized(self) -> bool:
        if self.framework.vk:
            return True
        return False

    @staticmethod
    def remove_dups(array: list) -> list:
        new = []
        for i in array:
            if i not in new:
                new.append(i)
        return new

    def get_captcha(self) -> bool:
        return not self.get_y_or_n()

    def get_group(self) -> int:
        group_id = str(input("Введите ID или screen_name сообщества: "))
        group_id = self.framework.get_community_by_id(group_id)
        try:
            self.framework.get_banned_members(group_id)
        except NNGFramework.exception_tuple as error:
            lg.log(
                self.name,
                f"Не удалось получить группу {group_id} из-за ошибки: {error}",
                2,
            )
            return self.get_group()
        if not group_id or group_id is None:
            lg.log("NNG Utils", "Недействтительный ID или screen_name", 2)
            return self.get_group()
        return group_id

    def get_user(self) -> int:
        user = str(input("Введите ID или screen_name пользователя: "))
        try:
            user = self.framework.vk.users.get(user_ids=user)[0]["id"]
        except self.framework.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}")
            return self.get_user()
        if not user or user is None:
            lg().log("NNG Utils", "Недействтительный ID или screen_name", 2)
            return self.get_user()
        return int(user)

    @staticmethod
    def get_y_or_n(
        promt: str = "Выполнять операцию без каптчи?",
    ) -> bool:
        var = str(input(f"{promt} (Y - Да, N - Нет): "))
        while var.lower() not in ["y", "n"]:
            var = str(input("(Y - Да, N - Нет): "))
        return var.lower() == "y"

    @operation
    def block(self, func: Function):
        rtype = func.fid
        data = NNGSaves().load()
        promt = "1. В сообществе\n\n2. В сообществах\n\n3. Вернуться назад"
        choose = self.helper.get_choose(promt, 3)
        if choose == 3:
            raise ReturnBack
        captcha = self.get_captcha()
        if rtype == 1:
            if not choose:
                raise IndentationError
            user = self.get_user()
            if choose == 1:
                group = self.get_group()
                self.framework.block(group, [user], data["com"], captcha=captcha)
            elif choose == 2:
                groups = self.framework.unarchive_groups()
                for group in groups:
                    self.framework.block(group, [user], data["com"], captcha=captcha)

        elif rtype == 2:
            if not choose:
                raise IndentationError
            users = self.framework.unarchive_banlist()
            if choose == 1:
                group = self.get_group()
                self.framework.block(group, users, data["com"], captcha=captcha)
            elif choose == 2:
                groups = self.framework.unarchive_groups()
                for group in groups:
                    self.framework.block_with_exception(
                        group, users, data["com"], captcha=captcha
                    )

        else:
            raise IndentationError

    @operation
    def unblock(self, func: Function):
        rtype = func.fid
        data = NNGSaves().load()
        promt = "1. В сообществе\n\n2. В сообществах\n\n3. Вернуться назад\n\n"
        choose = self.helper.get_choose(promt, 3)
        if choose == 3:
            raise ReturnBack
        if rtype == 1:
            if not choose:
                raise IndentationError
            user = self.get_user()
            if choose == 1:
                group = self.get_group()
                self.framework.unblock(group, [user], data["com"])
            elif choose == 2:
                groups = self.framework.unarchive_groups()
                for group in groups:
                    self.framework.unblock(group, [user], data["com"])
        elif rtype == 2:
            if not choose:
                raise IndentationError
            if choose == 1:
                group = self.get_group()
                users = self.framework.get_banned_members(group)
                self.framework.unblock(group, users, data["com"])
            elif choose == 2:
                promt = cf.bold_on_red(
                    "Вы абсолютно уверены в том, что хотите РАЗБАНИТЬ ВСЕХ пользователей во ВСЕХ сообществах?"
                )
                choose = self.helper.get_yn_choose(promt)
                if not choose:
                    raise IndentationError
                if choose == 1:
                    groups = self.framework.unarchive_groups()
                    for group in groups:
                        lg.log(self.name, f"Переходим к группе ID: {group}", 1)
                        users = self.framework.get_banned_members(group)
                        lg.log(
                            self.name,
                            f"Извлекли заблокированных пользователей ({len(users)})",
                        )
                        self.framework.unblock(group, users, data["com"])

        else:
            raise IndentationError

    @operation
    def manager(self, func: Function):
        rtype = func.fid
        load = self.helper.get_choose(
            "1. Пользователю\n\n2. Пользователям\n\n3. Вернуться назад", 3
        )
        if load == 3:
            raise ReturnBack(func)
        if rtype == 1:
            if load == 1:
                group = self.get_group()
                user = self.get_user()
                self.framework.editor(group=group, users=[user])

            elif load == 2:
                group = self.get_group()
                users = self.framework.get_all_community_members(
                    group=group, with_banned=False
                )
                lg.log(self.name, "Получили участников", 1)
                admins = self.framework.get_all_community_members(
                    group=group, managers=True
                )
                if not admins or admins is None:
                    lg.log(
                        self.name,
                        f"Не удалось получить участников сообщества {group}",
                        2,
                    )
                    return
                lg.log(self.name, "Получили администрацию", 1)
                users = [i for i in users if i not in admins]
                lg.log(self.name, f"Доступно к выдаче: {100-len(admins)}")
                if len(users) > 0:
                    lg.log(self.name, "Запущен процесс выдачи", 1)
                    self.framework.editor(
                        group=group, users=users, limit=(100 - len(admins)), clear=False
                    )

        elif rtype == 2:
            if load == 1:
                group = self.get_group()
                user = self.get_user()
                self.framework.editor(group=group, users=[user], clear=True)
            elif load == 2:
                group = self.get_group()
                members = self.framework.get_all_community_members(
                    group=group, managers=True
                )
                self.framework.editor(group=group, users=members, clear=True)
        else:
            raise IndentationError

    @operation
    def community(self, func: Function):
        rtype = func.fid
        data = NNGSaves().load()

        choose = self.helper.get_choose(
            "1. В сообществе\n\n2. В сообществах\n\n3. Вернуться назад",
            3,
        )
        if not choose:
            raise IndentationError
        if choose == 3:
            raise ReturnBack(func)
        if rtype == 1:

            def ban_check(community, banned_members):
                community = self.framework.get_community_by_id(community)
                banned = self.framework.ban_check(
                    group=community, banlist=banned_members
                )
                if banned is None:
                    lg.log(self.name, f"Нет прав на сообщество {community}", 2)
                    return []
                if len(banned) > 0:
                    lg.log(
                        self.name,
                        f"[Сообщество: {community}] Были найдены заблокированные руководители:\n{banned}",
                        2,
                    )
                    return banned
                lg.log(
                    self.name,
                    f"[Сообщество: {community}] Заблокированных руководителей найдено не было",
                )
                return []

            groups = (
                [self.get_group()] if choose == 1 else self.framework.unarchive_groups()
            )
            banlist = self.framework.unarchive_banlist(debug=False)
            if not banlist or banlist is None:
                lg.log(self.name, "Ошибка при распаковке бан-листа", 3)
                return
            group_data = {}
            for group in groups:
                group = self.framework.get_community_by_id(group)
                banned = ban_check(community=group, banned_members=banlist)
                if banned is not None and len(banned) > 0:
                    group_data[group] = banned
            if len(group_data) > 0:
                ask = self.get_y_or_n("Приступить к блокировке?")
                if ask:
                    captcha = self.get_captcha()
                    for key in group_data:
                        if group_data[key] is None or not group_data[key]:
                            continue
                        lg.log(
                            self.name, f"Приступаем к блокировке в сообществе {key}", 1
                        )
                        self.framework.editor(key, group_data[key], clear=True)
                        self.framework.block(key, group_data[key], data["com"], captcha)
        elif rtype == 2:
            groups = (
                [self.get_group()] if choose == 1 else self.framework.unarchive_groups()
            )
            user = self.get_user()
            for group in groups:
                members = self.framework.get_all_community_members(group)
                if not members:
                    lg.log(
                        self.name, f"Нет прав просмотр участников сообщества {group}", 3
                    )
                    continue
                if user in members:
                    lg.log(self.name, f"ID {user} найден в сообществе {group}", 2)
                else:
                    lg.log(self.name, f"ID {user} не найден в сообществе {group}", 1)

        else:
            raise IndentationError

    @operation
    def other(self, func: Function):
        rtype = func.fid
        if rtype == 1:
            message = str(input("Введите ID поста (в формате 'wall66748_3675'): "))
            groups = self.framework.unarchive_groups()
            for group in groups:
                self.framework.repost(group=group, message=message)
                lg.log(self.name, f"Пост в группу {group} готов!")

        elif rtype == 2:
            choose = self.helper.get_choose(
                promt="1. По ссылке\n\n2. Вручную\n\n3. Вернуться назад",
                maxValue=3,
            )
            if not choose:
                raise IndentationError

            if choose == 1:
                url = str(input("[NNG Utils] Введите ссылку на список: "))
                screen_names = urllib.request.urlopen(url).read().decode().split(", ")
                print(self.framework.get_user_ids(users=screen_names))

            elif choose == 2:
                scr = str(input("[NNG Utils] Введите screen_name: "))
                lg.log(self.name, f"ID: {self.framework.get_user_ids(user=scr)}", 1)

            elif choose == 3:
                raise ReturnBack(func)

        elif rtype == 3:
            choose = self.helper.get_choose(
                promt="1. Сообщества\n\n2. Сообществ\n\n3. Вернуться назад",
                maxValue=3,
            )
            if not choose:
                raise IndentationError

            if choose == 3:
                raise ReturnBack(func)

            groups = (
                [self.get_group()] if choose == 1 else self.framework.unarchive_groups()
            )
            for group in groups:
                self.framework.change_community_wall_state(group, True)
                posts = self.framework.get_community_posts(group)
                if len(posts) <= 0 or posts[0] == 0:
                    self.framework.change_community_wall_state(group, False)
                    lg.log(self.name, f"Посты в сообществе {group} отсутвуют", 2)
                    continue
                for post in posts:
                    result = self.framework.delete_community_post(group, post)
                    if result == 1:
                        lg.log(self.name, f"Удалили пост {post} в группе {group}")
                    else:
                        lg.log(
                            self.name,
                            f"Не удалось удалить пост {post} в группе {group}",
                            2,
                        )
                self.framework.change_community_wall_state(group, False)

        elif rtype == 4:
            groups = self.framework.unarchive_groups()
            stat = {
                "members": {"normal": 0, "clean": 0},
                "managers": {"normal": 0, "clean": 0},
            }
            for group in groups:
                lg.log(self.name, f"Обрабатываем группу: {group}")
                if not self.framework.if_user_is_community_admin(group):
                    lg.log(
                        self.name, "Невозможно проверить группу из-за отсутсвия прав", 2
                    )
                    continue
                members = self.framework.get_all_community_members(
                    group=group, managers=False
                )
                managers = self.framework.get_all_community_members(
                    group=group, managers=True
                )
                members_clean = self.framework.get_all_community_members(
                    group=group, with_banned=False, managers=False
                )
                managers_clean = self.framework.get_all_community_members(
                    group=group, managers=True, with_banned=False
                )
                members = self.remove_dups(members)
                managers = self.remove_dups(managers)
                members_clean = self.remove_dups(members_clean)
                managers_clean = self.remove_dups(managers_clean)
                stat["members"]["normal"] += len(members)
                stat["managers"]["normal"] += len(managers)
                stat["members"]["clean"] += len(members_clean)
                stat["managers"]["clean"] += len(managers_clean)
            lg.log(
                self.name,
                f"Вывод статистики:\n\nОбщее количество подписчиков:\n"
                f"С учетом заблокированных: {stat['members']['normal']}\n"
                f"Без учета заблокированных: {stat['members']['clean']}\n\n"
                f"Общее количество редакторов:\n"
                f"С учетом заблокированных: {stat['managers']['normal']}\n"
                f"Без учета заблокированных: {stat['managers']['clean']}\n\n"
                f"Максимальное количество руководителей: {len(self.framework.unarchive_groups())*100}",
                2,
            )

        elif rtype == 5:
            NNGSaves().dialog(function=func)

    @operation
    @staticmethod
    def saves():
        NNGSaves().dialog()
