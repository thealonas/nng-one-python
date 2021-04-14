# -*- coding: utf-8 -*-
import vk_api
import webbrowser
import urllib.request
import colorful as cf
from time import sleep
from typing import Union
from logger import Logger as lg
from framework.saves import NNGSaves
from other.cmd_helper import CMDHelper


class NNGFramework:
    name = "NNG Framework"
    exception_tuple = (
        vk_api.ApiError,
        vk_api.VkApiError,
        vk_api.ApiHttpError,
        vk_api.AuthError,
        vk_api.TwoFactorError,
        vk_api.exceptions.Captcha,
        vk_api.exceptions.ApiError,
        vk_api.exceptions.VkApiError,
        vk_api.exceptions.ApiHttpError,
        vk_api.exceptions.AuthError,
        vk_api.exceptions.TwoFactorError,
    )

    def __init__(self, token):
        self.vk = self.auth_msg = None
        self.auth = self.auth(token)
        self.debug = False

    def auth(self, token) -> bool:
        try:
            token = vk_api.VkApi(token=token)
            self.vk = token.get_api()
            name = self.vk.account.getProfileInfo()
            surname = name.get("last_name")
            userid = name.get("id")
            name = name.get("first_name")
            self.auth_msg = f"[Auth] Авторизован по токену | Добро пожаловать, {name} {surname} | ID: {userid}"
            return True
        except self.exception_tuple as Error:
            lg().log(self.name, "[Auth] Ошибка авторизации: {}".format(Error), 3)
            self.vk = None
            return False

    def get_auth_msg(self):
        return self.auth_msg

    def get_user_ids(self, user: str = None, users: list = None):
        try:
            if user:
                answer = self.vk.users.get(user_ids=user)
                if type(answer) is list:
                    answer = answer[0]["id"]
                    return answer
                raise ValueError(f"ID пользователя {user} не найден")
            if users:
                answer = self.vk.users.get(user_ids=users)
                ids = []
                for query in answer:
                    ids.append(query["id"])
                return ids
            return False
        except vk_api.exceptions.Captcha as captcha:
            self.captcha_handler(captcha)
        except self.exception_tuple as Error:
            lg().log(self.name, "Неизвестная ошибка! {0}".format(Error), 3)
            return False

    def get_community_by_id(self, name: Union[str, int]):
        try:
            group = self.vk.groups.getById(group_id=name)
            return group[0]["id"]
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)

    def captcha_handler(self, captcha):
        webbrowser.open_new(captcha.get_url())
        key = input(
            cf.bold_green(
                f"[NNG Framework] [Captcha Handler] Введите код каптчи: {captcha.get_url()}: "
            )
        )
        try:
            captcha.try_again(key)
        except vk_api.exceptions.Captcha as captcha:
            lg.log(
                self.name,
                "[Captcha Handler] Неправильный ввод каптчи! Попробуйте снова.",
                3,
            )
            self.captcha_handler(captcha)

    def unarchive_banlist(self, debug: bool = False):
        saves = NNGSaves().load()
        rtype = saves["lists"]["loadtype"]
        banlist = saves["lists"]["banlist"]
        urllib.request.urlcleanup()
        try:
            if rtype == "0":
                objects = urllib.request.urlopen(banlist).read().decode().split(",")
                for index in range(len(objects)):
                    objects[index] = int(objects[index])
                if debug:
                    print(objects)
                    print(type(objects[0]))
                return objects
            if rtype == "1":
                with open(banlist, "r") as f:
                    objects = f.read().split(",")
                for index in range(len(objects)):
                    objects[index] = int(objects[index])
                if debug:
                    print(objects)
                    print(type(objects[0]))
                return objects
        except self.exception_tuple as Error:
            lg.log(self.name, f"Произошла ошибка: {Error}", 3)
            return False

    def unarchive_groups(self):
        saves = NNGSaves().load()
        rtype = saves["lists"]["loadtype"]
        group_list = saves["lists"]["grouplist"]
        try:
            objects = []
            if rtype == "0":
                objects = urllib.request.urlopen(group_list).read().decode().split(",")
            if rtype == "1":
                with open(group_list, "r") as f:
                    objects = f.read().split(",")
            for index in range(len(objects)):
                objects[index] = int(objects[index])
            return objects
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            return False

    # [-- Group management --]

    def if_user_is_community_editor(self, group: int) -> bool:
        try:
            banned = self.get_banned_members(group=group)
            if banned is None:
                return False
            return True
        except vk_api.exceptions.Captcha:
            sleep(10)
            return self.if_user_is_community_editor(group)
        except self.exception_tuple:
            return False

    def if_user_is_community_admin(self, group: int) -> bool:
        try:
            managers = self.get_all_community_members(group=group, managers=True)
            if managers is None:
                return False
            return True
        except vk_api.exceptions.Captcha:
            sleep(10)
            return self.if_user_is_community_admin(group)
        except self.exception_tuple:
            return False

    def delete_community_post(self, group: int, post: int) -> bool:
        try:
            self.vk.wall.delete(owner_id=-group, post_id=post)
            return True
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            return False

    def get_community_posts(self, group: int) -> list[int]:
        posts = self.vk.wall.get(owner_id=-group)["items"]
        for index in range(len(posts)):
            posts[index] = posts[index]["id"]
        return posts

    def change_community_wall_state(self, group: int, state: bool):
        try:
            self.vk.groups.edit(group_id=group, wall=2 if state else 0)
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)

    def get_banned_members(self, group: int):
        banned_users = []
        try:
            count = self.vk.groups.getBanned(group_id=group, count=1)["count"]
            count = count // 200 if count >= 200 else count // 200 + 1
            for index in range(0, count + 1):
                items = self.vk.groups.getBanned(
                    group_id=group, count=200, offset=index * 200
                )["items"]
                banned_users.append(items)
            ids = []
            for index in range(len(banned_users)):
                for second_index in range(len(banned_users[index])):
                    ids.append(banned_users[index][second_index])
            banned_users = ids
            for index in range(len(banned_users)):
                banned_users[index] = banned_users[index]["profile"]["id"]
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            return None
        return banned_users

    def get_all_community_members(
        self, group: int, managers: bool = False, with_banned: bool = True
    ) -> list[int]:
        members = []
        try:
            count = self.vk.groups.getMembers(
                group_id=group, filter="managers" or None, count=0
            )["count"]
            count = count // 1000 if count >= 1000 else count // 1000 + 1
            for index in range(0, count + 1):
                items = self.vk.groups.getMembers(
                    group_id=group,
                    count=1000,
                    offset=index * 1000 if index != 0 else None,
                    sort="time_asc",
                    fields="sex",
                    filter="managers" if managers else None,
                )
                items = items["items"]
                if not with_banned:
                    listing = []
                    for profile in items:
                        if "deactivated" not in profile.keys():
                            listing.append(profile)
                    members += listing
                else:
                    members += items
            ids = []
            for profile in members:
                ids.append(profile["id"])
            return ids
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            return None

    def repost(self, group: int, message: str):
        try:
            self.vk.wall.repost(group_id=group, object=message)
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)

    def block_with_exception(
        self, group: int, banlist: list[int], com: str, captcha: bool = True
    ):
        banned_users = self.get_banned_members(group)
        banlist = [i for i in banlist if i not in banned_users]
        counter = 0
        while counter < len(banlist):
            user = banlist[counter]
            response = 0
            try:
                response = self.vk.groups.ban(
                    group_id=group, owner_id=user, comment=com, comment_visible=1
                )
            except vk_api.exceptions.Captcha as capt:
                if captcha:
                    try:
                        self.captcha_handler(capt)
                    except self.exception_tuple:
                        pass
                else:
                    lg.log(self.name, "Пауза на 15 секунд", 2)
                    counter -= 1
                    sleep(15)
            except self.exception_tuple as Error:
                lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            if response == 1:
                lg.log(
                    self.name, f"ID {user} добавлен в черный список сообщества {group}"
                )
            else:
                lg.log(
                    self.name,
                    f"ID {user} не добавлен в черный список сообщества {group}",
                    2,
                )
            counter += 1

    def block(self, group: int, banlist: list[int], com: str, captcha: bool = True):
        counter = 0
        while counter < len(banlist):
            user = banlist[counter]
            response = 0
            try:
                response = self.vk.groups.ban(
                    group_id=group, owner_id=user, comment=com, comment_visible=1
                )
            except vk_api.exceptions.Captcha as capt:
                if captcha:
                    self.captcha_handler(capt)
                else:
                    lg.log(self.name, "Пауза на 15 секунд", 2)
                    counter -= 1
                    sleep(15)
            except self.exception_tuple as Error:
                lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            if response == 1:
                lg.log(
                    self.name, f"ID {user} добавлен в черный список сообщества {group}"
                )
            else:
                lg.log(
                    self.name,
                    f"ID {user} не добавлен в черный список сообщества {group}",
                    2,
                )
            counter += 1

    def unblock(self, group: int, ban_list: list[int], captcha: bool = True):
        for user in ban_list:
            response = 0
            try:
                response = self.vk.groups.unban(group_id=group, owner_id=user)
            except vk_api.exceptions.Captcha as capt:
                if captcha:
                    self.captcha_handler(capt)
                else:
                    lg.log(self.name, "Пауза на 15 секунд", 2)
                    sleep(15)
            except self.exception_tuple as Error:
                lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            if response == 1:
                lg.log(
                    self.name, f"ID {user} убран из черного списка сообщества {group}"
                )
            else:
                lg.log(
                    self.name,
                    f"Не удалось убрать ID {user} из черного списка сообщества {group}",
                    2,
                )

    def editor(
        self, group: int, users: list[int], limit: int = 100, clear: bool = False
    ):
        task_sleep = 7200
        captcha_count = managers_count = 0
        helper = CMDHelper()
        is_sleeping = passing_manager = False
        counter = 0
        while counter < len(users):
            response = 0
            user = users[counter]
            try:
                response = self.vk.groups.editManager(
                    group_id=group,
                    user_id=user,
                    role=None if clear else "editor",
                    is_contact=0,
                )
            except vk_api.exceptions.Captcha as capt:
                captcha_count += 1
                response = 1
                if captcha_count == 1:
                    lg.log(
                        self.name, "Похоже, что ВКонтакте начал запрашивать каптчу", 2
                    )
                    ask = "1. Подождать\n\n2. Продолжить ввод капчи\n\n3. Остановить выдачу"
                    choose = helper.get_choose(ask, 3)
                    if choose == 1:
                        is_sleeping = True
                    elif choose == 2:
                        is_sleeping = False
                    else:
                        lg.log(self.name, "Выходим из операции")
                        break
                if is_sleeping:
                    lg.log(self.name, f"Пауза на {task_sleep} секунд")
                    counter -= 1
                    sleep(task_sleep)
                else:
                    self.captcha_handler(capt)
                    passing_manager = True
                    counter -= 1
            except self.exception_tuple as Error:
                lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
            if response == 1 and not passing_manager:
                lg.log(
                    self.name,
                    f"ID {user} {'убран из менеджеров' if clear else 'добавлен в редакторы'} сообщества {group}",
                )
                managers_count += 1
            elif not passing_manager:
                lg.log(
                    self.name,
                    f"ID {user} не удалось {'убрать из менеджеров' if clear else 'добавить в редакторы'} сообщества {group}",
                    2,
                )
            if managers_count >= limit:
                break
            counter += 1
            passing_manager = False

    def ban_check(self, group: int, banlist: list[int]):
        try:
            managers = self.get_all_community_members(
                group=group,
                managers=True,
                with_banned=False,
            )
            if managers is None:
                return None
            banned = [i for i in managers if i in banlist]
            return banned
        except vk_api.exceptions.Captcha:
            lg.log(self.name, "Пауза на 15 секунд", 2)
            sleep(15)
            return self.ban_check(group, banlist)
        except self.exception_tuple as Error:
            lg.log(self.name, f"Неизвестная ошибка: {Error}", 3)
