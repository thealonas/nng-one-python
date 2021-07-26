# -*- coding: utf-8 -*-
import typing
import colorful as cf
import urllib.request
from urllib.error import HTTPError
from framework.api import NNGFramework
from framework.functions import Function
from framework.functions import operation
from framework.saves import NNGSaves
from utils.logger import Logger as lg
from other.cmd_helper import CMDHelper
from other.exceptions import ReturnBack


class NNGCore:
    name = "NNG Core"

    class callback_operations:
        editor = 1
        block = 2
        unblock = 3
        wall = 4

    def __init__(self, token):
        self.framework = NNGFramework(token)
        self.msg = self.framework.get_auth_msg()
        self.data = NNGSaves()
        self.helper = CMDHelper()
        self.messages = None

    def is_authorized(self) -> bool:
        if self.framework.vk:
            return True
        return False

    def set_messages(self, messages: typing.List[dict]):
        self.messages = messages

    @staticmethod
    def remove_duplicates(array: list) -> list:
        new = []
        for i in array:
            if i not in new:
                new.append(i)
        return new

    def get_group(self) -> int:
        group_id = str(input(cf.bold_blue("Введите ID или screen_name сообщества: ")))
        group_id = self.framework.get_community_by_id(group_id)
        if not self.framework.assure_community_ownership(group_id):
            lg.log(
                f"Не удалось проверить владение сообществом {group_id}",
                lg.level.warn,
                self.name,
            )
            return self.get_group()
        return group_id

    def get_user(self) -> int:
        user = str(input(cf.bold_blue("Введите ID или screen_name пользователя: ")))
        try:
            user = self.framework.vk.users.get(user_ids=user)[0]["id"]
        except Exception as Error:
            lg.log(f"Неизвестная ошибка: {Error}", lg.level.error, name=self.name)
            return self.get_user()
        if not user or user is None:
            lg.log("Неверный ID или screen_name", lg.level.error, name=self.name)
            return self.get_user()
        return int(user)

    def if_community_has_more_equal_50_members(self, group: int) -> bool:
        return len(self.framework.get_all_community_members(group)) >= 50

    def switch_callback(self, group: int, setting: int, state: bool):
        """
        В отличии от метода из api.py, этот метод проверяет на наличие switch_callback в config.json
        """
        callback = self.data.callback
        if callback:
            state = 1 if state else 0
            servers = self.framework.get_community_callback_servers(group=group)
            if len(servers) > 0:
                lg.log(
                    f'Пытаемся изменить настройку Callback с номером "{setting}" в группе {group} на {state}',
                    lg.level.debug,
                )
                for server in servers:
                    if setting == self.callback_operations.editor:
                        self.framework.change_community_callback_editor_state(
                            group, server, state
                        )
                    elif setting == self.callback_operations.block:
                        self.framework.change_community_callback_banned_state(
                            group, server, state
                        )
                    elif setting == self.callback_operations.unblock:
                        self.framework.change_community_callback_unbanned_state(
                            group, server, state
                        )
                    elif setting == self.callback_operations.wall:
                        self.framework.change_community_callback_wall_states(
                            group, server, state
                        )
            else:
                lg.log(
                    "Операция не выполена, так как отсутсвуют сервер Callback API Бот",
                    lg.level.debug,
                )
        return False

    @staticmethod
    def get_y_or_n(
        prompt: str = "Выполнить операцию без каптчи?",
    ) -> bool:
        var = str(input(f"{prompt} (Y - Да, N - Нет): "))
        while var.lower() not in ["y", "n"]:
            var = str(input("(Y - Да, N - Нет): "))
        return var.lower() == "y"

    @operation
    def block(self, func: Function):
        rtype = func.fid
        prompt = "1. В сообществе\n\n2. В сообществах\n\n3. Вернуться назад"
        choose = self.helper.get_menu_choose(prompt, 3, messages=self.messages)
        if choose == 3:
            raise ReturnBack(func)
        if rtype == 1:
            if not choose:
                raise IndentationError
            user = self.get_user()
            if choose == 1:
                group = self.get_group()
                lg.clear()
                self.framework.block(group, [user], self.data.comment)
            elif choose == 2:
                lg.clear()
                groups = self.framework.unpack_group_list()
                for group in groups:
                    if not self.framework.assure_community_ownership(group):
                        lg.log(
                            f"Отсутствуют права на сообщество {group}", tp=lg.level.warn
                        )
                        continue
                    group = self.framework.get_community_by_id(group)
                    self.switch_callback(
                        group=group, setting=self.callback_operations.block, state=False
                    )
                    self.switch_callback(
                        group=group,
                        setting=self.callback_operations.editor,
                        state=False,
                    )
                    editors = self.framework.ban_check(group, [user])
                    self.framework.editor(
                        group, editors, limit=len(editors), clear=True, debug=True
                    )
                    self.framework.block(group, [user], self.data.comment)
                    self.switch_callback(
                        group=group, setting=self.callback_operations.block, state=True
                    )
                    self.switch_callback(
                        group=group, setting=self.callback_operations.editor, state=True
                    )

        elif rtype == 2:
            if not choose:
                raise IndentationError
            users = self.framework.unpack_ban_list()
            if choose == 1:
                group = self.get_group()
                lg.clear()
                group = self.framework.get_community_by_id(group)
                self.switch_callback(
                    group=group, setting=self.callback_operations.block, state=False
                )
                self.switch_callback(
                    group=group, setting=self.callback_operations.editor, state=False
                )
                editors = self.framework.ban_check(group, users)
                self.framework.editor(
                    group, editors, limit=len(editors), clear=True, debug=True
                )
                self.framework.block(group, users, self.data.comment)
                self.switch_callback(
                    group=group, setting=self.callback_operations.editor, state=True
                )
                self.switch_callback(
                    group=group, setting=self.callback_operations.block, state=True
                )
            elif choose == 2:
                lg.clear()
                groups = self.framework.unpack_group_list()
                for group in groups:
                    if not self.framework.assure_community_ownership(group):
                        lg.log(
                            f"Отсутствуют права на сообщество {group}", tp=lg.level.warn
                        )
                        continue
                    group = self.framework.get_community_by_id(group)
                    self.switch_callback(
                        group=group, setting=self.callback_operations.block, state=False
                    )
                    self.switch_callback(
                        group=group,
                        setting=self.callback_operations.editor,
                        state=False,
                    )
                    editors = self.framework.ban_check(group, users)
                    self.framework.editor(
                        group, editors, limit=len(editors), clear=True, debug=True
                    )
                    self.framework.block(group, users, self.data.comment)
                    self.switch_callback(
                        group=group, setting=self.callback_operations.editor, state=True
                    )
                    self.switch_callback(
                        group=group, setting=self.callback_operations.block, state=True
                    )

        else:
            raise IndentationError

    @operation
    def unblock(self, func: Function):
        rtype = func.fid
        prompt = "1. В сообществе\n\n2. В сообществах\n\n3. Вернуться назад"
        choose = self.helper.get_menu_choose(prompt, 3, messages=self.messages)
        if choose == 3:
            raise ReturnBack(func)
        if rtype == 1:
            if not choose:
                raise IndentationError
            user = self.get_user()
            if choose == 1:
                group = self.get_group()
                lg.clear()
                self.framework.unblock(group, [user], self.data.captcha_ban)
            elif choose == 2:
                lg.clear()
                groups = self.framework.unpack_group_list()
                for group in groups:
                    if not self.framework.assure_community_ownership(group):
                        lg.log(
                            f"Отсутствуют права на сообщество {group}", tp=lg.level.warn
                        )
                        continue
                    self.switch_callback(
                        group=group,
                        setting=self.callback_operations.unblock,
                        state=False,
                    )
                    self.framework.unblock(group, [user], self.data.captcha_ban)
                    self.switch_callback(
                        group=group,
                        setting=self.callback_operations.unblock,
                        state=True,
                    )
        elif rtype == 2:
            if not choose:
                raise IndentationError
            if choose == 1:
                group = self.get_group()
                lg.clear()
                users = self.framework.get_banned_members(group)
                self.switch_callback(
                    group=group,
                    setting=self.callback_operations.unblock,
                    state=False,
                )
                self.framework.unblock(group, users, self.data.captcha_ban)
                self.switch_callback(
                    group=group,
                    setting=self.callback_operations.unblock,
                    state=True,
                )
            elif choose == 2:
                prompt = cf.bold_on_red(
                    "Вы уверены в том, что хотите разблокировать ВСЕХ пользователей во ВСЕХ сообществах?"
                )
                choose = self.helper.get_yn_choose(prompt)
                if choose:
                    lg.clear()
                    groups = self.framework.unpack_group_list()
                    for group in groups:
                        lg.log(
                            f"Переходим к группе ID: {group}", lg.level.debug, self.name
                        )
                        if not self.framework.assure_community_ownership(group):
                            lg.log(
                                f"Отсутствуют права на сообщество {group}",
                                tp=lg.level.warn,
                            )
                            continue
                        users = self.framework.get_banned_members(group)
                        lg.log(
                            f"Извлекли заблокированных пользователей ({len(users)})",
                            lg.level.debug,
                            self.name,
                        )
                        self.switch_callback(
                            group=group,
                            setting=self.callback_operations.unblock,
                            state=False,
                        )
                        self.framework.unblock(group, users, self.data.captcha_ban)
                        self.switch_callback(
                            group=group,
                            setting=self.callback_operations.unblock,
                            state=True,
                        )
                else:
                    raise ReturnBack(func)
        else:
            raise IndentationError

    @operation
    def manager(self, func: Function):
        rtype = func.fid
        load = self.helper.get_menu_choose(
            "1. Пользователю\n\n2. Пользователям\n\n3. Вернуться назад",
            3,
            messages=self.messages,
        )
        if load == 3:
            raise ReturnBack(func)
        group = self.get_group()
        try:
            if not self.if_community_has_more_equal_50_members(
                group
            ) and not self.helper.get_yn_choose(
                "В Вашем сообществе меньше 50 участников. Продолжить?"
            ):
                return
        except Exception as Error:
            lg.log(f"Произошла ошибка: {Error}", lg.level.error, self.name)
        if rtype == 1:
            if load == 1:
                user = self.get_user()
                lg.clear()
                self.framework.editor(group=group, users=[user])
            elif load == 2:
                lg.clear()
                users = self.framework.get_all_community_members(
                    group=group, with_banned=False
                )
                lg.log("Получили участников", lg.level.debug, self.name)
                admins = self.framework.get_all_community_members(
                    group=group, managers=True
                )
                if not admins or admins is None:
                    lg.log(
                        f"Не удалось получить участников сообщества {group}",
                        2,
                        self.name,
                    )
                    return
                lg.log("Получили руководителей", lg.level.debug, self.name)
                users = [i for i in users if i not in admins]
                lg.log(
                    f"Доступно к выдаче: {100 - len(admins)}",
                    lg.level.success,
                    self.name,
                )
                self.switch_callback(
                    group=group, setting=self.callback_operations.editor, state=False
                )
                if len(users) > 0:
                    lg.log("Запущен процесс выдачи", lg.level.debug, self.name)
                    self.framework.editor(
                        group=group, users=users, limit=(100 - len(admins)), clear=False
                    )
                self.switch_callback(
                    group=group, setting=self.callback_operations.editor, state=True
                )
        elif rtype == 2:
            if load == 1:
                user = self.get_user()
                lg.clear()
                self.framework.editor(group=group, users=[user], clear=True)
            elif load == 2:
                lg.clear()
                members = self.framework.get_all_community_members(
                    group=group, managers=True
                )
                self.switch_callback(
                    group=group, setting=self.callback_operations.editor, state=False
                )
                self.framework.editor(group=group, users=members, clear=True)
                self.switch_callback(
                    group=group, setting=self.callback_operations.editor, state=True
                )
        else:
            raise IndentationError

    @operation
    def community(self, func: Function):
        rtype = func.fid
        choose = self.helper.get_menu_choose(
            "1. В сообществе\n\n2. В сообществах\n\n3. Вернуться назад",
            3,
            messages=self.messages,
        )
        if not choose:
            raise IndentationError
        if choose == 3:
            raise ReturnBack(func)

        groups = (
            [self.get_group()] if choose == 1 else self.framework.unpack_group_list()
        )
        if rtype == 1:
            lg.clear()
            unpacked_ban_list = self.framework.unpack_ban_list()
            group_data = {}
            for group in groups:
                if not self.framework.assure_community_ownership(group):
                    lg.log(
                        f"Отсутствуют права на сообщество {group}",
                        tp=lg.level.warn,
                        force=True,
                    )
                    continue
                lg.log(f"Переходим к сообществу {group}")
                group = self.framework.get_community_by_id(group)
                banned = self.framework.ban_check(group, unpacked_ban_list)
                if banned is not None and len(banned) > 0:
                    lg.log(
                        f"В сообществе {group} были найдены заблокированные руководители",
                        lg.level.warn,
                        self.name,
                        force=True,
                    )
                    group_data[group] = banned
            if len(group_data) > 0:
                ask = self.get_y_or_n("Приступить к блокировке?")
                if ask:
                    lg.clear()
                    for key in group_data:
                        if group_data[key] is None or not group_data[key]:
                            continue
                        key = self.framework.get_community_by_id(key)
                        lg.log(
                            f"Приступаем к блокировке в сообществе {key}",
                            lg.level.success,
                            self.name,
                        )
                        self.switch_callback(
                            group=key,
                            setting=self.callback_operations.block,
                            state=False,
                        )
                        self.switch_callback(
                            group=key,
                            setting=self.callback_operations.editor,
                            state=False,
                        )
                        self.framework.editor(
                            key, group_data[key], clear=True, debug=True
                        )
                        self.framework.block(
                            key, group_data[key], self.data.comment, debug=True
                        )
                        self.switch_callback(
                            group=key,
                            setting=self.callback_operations.block,
                            state=True,
                        )
                        self.switch_callback(
                            group=key,
                            setting=self.callback_operations.editor,
                            state=True,
                        )
            else:
                lg.log("Заблокированных руководителей не было найдено", name=self.name)
        elif rtype == 2:
            user = self.get_user()
            lg.clear()
            for group in groups:
                members = self.framework.get_all_community_members(group, managers=True)
                if not members:
                    lg.log(
                        f"Нет прав на просмотр участников сообщества {group}",
                        3,
                        self.name,
                    )
                    continue
                if user in members:
                    lg.log(f"ID {user} найден в сообществе {group}", 2, self.name)
                else:
                    lg.log(f"ID {user} не найден в сообществе {group}", 1, self.name)

        else:
            raise IndentationError

    @operation
    def other(self, func: Function):
        rtype = func.fid
        if rtype == 1:
            message = self.helper.get_string_choose(
                "Введите ID поста (в формате 'wall-147811741_1600'): "
            )
            lg.clear()
            groups = self.framework.unpack_group_list()
            for group in groups:
                if not self.framework.assure_community_ownership(group):
                    lg.log(f"Отсутствуют права на сообщество {group}", tp=lg.level.warn)
                    continue
                self.switch_callback(
                    group=group, setting=self.callback_operations.wall, state=False
                )
                if self.framework.repost(group=group, message=message):
                    lg.log(f"Пост в группу {group} готов!", name=self.name)
                else:
                    lg.log(
                        f"Не удалось сделать пост в группу {group}",
                        lg.level.warn,
                        name=self.name,
                    )
                self.switch_callback(
                    group=group, setting=self.callback_operations.wall, state=True
                )

        elif rtype == 2:
            choose = self.helper.get_menu_choose(
                show_string="1. По ссылке\n\n2. Вручную\n\n3. Вернуться назад",
                maxValue=3,
                messages=self.messages,
            )
            if not choose:
                raise IndentationError

            if choose == 1:
                url = self.helper.get_string_choose(
                    "[NNG Utils] Введите ссылку на список: "
                )
                lg.clear()
                try:
                    screen_names = (
                        urllib.request.urlopen(url).read().decode().split(", ")
                    )
                except (ValueError, HTTPError):
                    lg.log("Невозможно получить список из этой ссылки…", tp=2)
                    return
                answer = self.framework.get_user_ids(users=screen_names)
                lg.log(f"Ответ: {answer}" if answer else "Ошибка во введённом URL")

            elif choose == 2:
                scr = self.helper.get_string_choose("[NNG Utils] Введите screen_name: ")
                lg.clear()
                answer = self.framework.get_user_ids(users=[scr])
                lg.log(f"Ответ: {answer}" if answer else "Ошибка VK API")
                if not answer:
                    lg.log(f"Ответ API: {answer}", lg.level.debug)

            elif choose == 3:
                raise ReturnBack(func)

        elif rtype == 3:
            choose = self.helper.get_menu_choose(
                show_string="1. Сообщества\n\n2. Сообществ\n\n3. Вернуться назад",
                maxValue=3,
                messages=self.messages,
            )
            if not choose:
                raise IndentationError

            if choose == 3:
                raise ReturnBack(func)
            if choose == 1:
                groups = [self.get_group()]
            else:
                groups = self.framework.unpack_group_list()
            lg.clear()
            for group in groups:
                if not self.framework.assure_community_ownership(group):
                    lg.log(f"Отсутствуют права на сообщество {group}", tp=lg.level.warn)
                    continue
                self.switch_callback(
                    group, setting=self.callback_operations.wall, state=False
                )
                self.framework.change_community_wall_state(group, True)
                posts = self.framework.get_community_posts(group)
                if len(posts) <= 0:
                    self.framework.change_community_wall_state(group, False)
                    lg.log(f"Посты в сообществе {group} отсутвуют", 2, self.name)
                    continue
                for post in posts:
                    result = self.framework.delete_community_post(group, post)
                    if result == 1:
                        lg.log(f"Удалили пост {post} в группе {group}", name=self.name)
                    else:
                        lg.log(
                            f"Не удалось удалить пост {post} в группе {group}",
                            2,
                            self.name,
                        )
                self.framework.change_community_wall_state(group, False)
                self.switch_callback(
                    group, setting=self.callback_operations.wall, state=True
                )

        elif rtype == 4:
            groups = self.framework.unpack_group_list()
            stat = {
                "members": {"normal": [], "clean": []},
                "managers": {"normal": [], "clean": []},
            }
            lg.clear()
            for group in groups:
                lg.log(f"Обрабатываем группу: {group}", name=self.name)
                if not self.framework.assure_community_ownership(group):
                    lg.log(
                        "Невозможно проверить группу из-за отсутсвия прав", 2, self.name
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
                stat["members"]["normal"] += members
                stat["managers"]["normal"] += managers
                stat["members"]["clean"] += members_clean
                stat["managers"]["clean"] += managers_clean
            lg.clear()
            lg.log(
                f"Вывод статистики:\n\nОбщее количество подписчиков: {len(stat['members']['normal'])}\n"
                f"Без учёта дубликатов: {len(self.remove_duplicates(stat['members']['normal']))}\n"
                f"Без учёта заблокированных: {len(stat['members']['clean'])}\n"
                f"Без учёта заблокированных и дубликатов: {len(self.remove_duplicates(stat['members']['clean']))}\n\n"
                f"Общее количество руководителей: {len(stat['managers']['normal'])}\n"
                f"Без учёта дубликатов: {len(self.remove_duplicates(stat['managers']['normal']))}\n"
                f"Без учёта заблокированных: {len(stat['managers']['clean'])}\n"
                f"Без учёта заблокированных и дубликатов: {len(self.remove_duplicates(stat['managers']['clean']))}\n\n"
                f"Максимальное количество руководителей: {len(self.framework.unpack_group_list()) * 100}",
                1,
                self.name,
            )

        elif rtype == 5:
            NNGSaves().dialog(function=func)

    @operation
    def saves(self):
        NNGSaves().dialog(self.messages)
