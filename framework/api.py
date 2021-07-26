# -*- coding: utf-8 -*-
import vk_api
import typing
import webbrowser
import urllib.request
import colorful as cf
from time import sleep
from typing import Union
from urllib.error import HTTPError
from framework.saves import NNGSaves
from utils.logger import Logger as lg


class NNGFramework:
    name = "NNG Framework"
    exception_tuple = (
        vk_api.exceptions.Captcha,
        vk_api.exceptions.ApiError,
        vk_api.exceptions.VkApiError,
        vk_api.exceptions.ApiHttpError,
        vk_api.exceptions.AuthError,
        vk_api.exceptions.TwoFactorError,
        TypeError,
    )

    class Exceptions:
        class BadLists(Exception):
            pass

    def __init__(self, token):
        self.vk = self.auth_msg = None
        self.auth(token)
        self.debug = False
        self.saves = NNGSaves()

    def auth(self, token) -> bool:
        try:
            token = vk_api.VkApi(token=token)
            self.vk = token.get_api()
            name = self.vk.account.getProfileInfo()
            userid = name.get("id")
            name = name.get("first_name")
            self.auth_msg = f"Добро пожаловать, {name} | Ваш ID: {userid}"
            return True
        except self.exception_tuple:
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
        except vk_api.exceptions.Captcha:
            sleep(5)
            return self.get_user_ids(user=user, users=users)
        except self.exception_tuple as Error:
            lg().log("Неизвестная ошибка! {0}".format(Error), 3, self.name)
            return False

    def get_user_by_id(self, name: Union[str, int]):
        try:
            user = self.vk.users.get(user_ids=name)
            return int(user[0]["id"])
        except Exception as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return False

    def get_community_by_id(self, name: Union[str, int]):
        try:
            group = self.vk.groups.getById(group_id=name)
            return int(group[0]["id"])
        except Exception as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return False

    def captcha_handler(self, captcha):
        webbrowser.open_new(captcha.get_url())
        key = input(
            cf.bold_green(
                f"[NNG Framework] [Captcha Handler] Введите код каптчи: {captcha.get_url()}: "
            )
        )
        try:
            return captcha.try_again(key)
        except vk_api.exceptions.Captcha as capt:
            lg.log(
                "[Captcha Handler] Неверный код каптчи! Попробуйте снова.",
                3,
                self.name,
            )
            self.captcha_handler(capt)

    def __unpack(self, rtype: int, url: str) -> [typing.List[str], None]:
        try:
            if rtype == 0:
                return urllib.request.urlopen(url).read().decode().split(",")
            if rtype == 1:
                with open(url, "r") as f:
                    return f.read().split(",")
        except (FileNotFoundError, HTTPError) as e:
            lg.log(f"Произошла ошибка: {e}", lg.level.debug)
            raise self.Exceptions.BadLists
        return None

    def __int_list(self, element: typing.List[str]) -> typing.List[int]:
        result = []
        for _, item in enumerate(element):
            try:
                result.append(int(item))
            except ValueError:
                lg.log(
                    f"Невозможно преобразовать {item} в число!",
                    lg.level.error,
                    force=True,
                )
                raise self.Exceptions.BadLists
        return result

    def unpack_ban_list(self):
        rtype = self.saves.load_type
        ban_list = self.saves.ban_list
        urllib.request.urlcleanup()
        try:
            unpacked = self.__unpack(rtype, ban_list)
            return self.__int_list(unpacked)
        except self.Exceptions.BadLists:
            lg.log("Невозможно распаковать списки!", tp=lg.level.error, name=self.name)
            raise NNGSaves.Exceptions.BadData

    def unpack_group_list(self):
        rtype = self.saves.load_type
        group_list = self.saves.group_list
        try:
            unpacked = self.__unpack(rtype, group_list)
            return self.__int_list(unpacked)
        except self.Exceptions.BadLists:
            lg.log("Невозможно распаковать списки!", tp=lg.level.error, name=self.name)
            raise NNGSaves.Exceptions.BadData

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

    def delete_community_post(self, group: int, post: int) -> bool:
        try:
            self.vk.wall.delete(owner_id=-group, post_id=post)
            return True
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return False

    def get_community_posts(self, group: int) -> typing.Union[typing.List[int], None]:
        try:
            posts_count = int(self.vk.wall.get(owner_id=-group, count=1)["count"])
            count = 1 if posts_count < 100 else (posts_count // 100) + 1
            posts = []
            for index in range(count):
                to_add = []
                post = self.vk.wall.get(
                    owner_id=-group, count=100, offset=index * 100, extended=False
                )["items"]
                for item in post:
                    if int(item["id"]) > 0:
                        to_add.append(item["id"])
                if len(to_add) > 0:
                    posts.append(to_add)
            posts = self.__remove_included_list(posts)
            output = []
            for _, element in enumerate(posts):
                try:
                    output.append(int(element))
                except ValueError:
                    continue
            return output
        except vk_api.exceptions.Captcha:
            sleep(10)
            return self.get_community_posts(group)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return None

    def get_community_callback_servers(
        self, group: int, callback_bot_only: bool = True
    ):
        try:
            servers = self.vk.groups.getCallbackServers(group_id=group)
            servers = servers["items"]
            result = []
            for server, element in enumerate(servers):
                if "cbbot.ifx.su" not in element["url"] and callback_bot_only:
                    lg.log(
                        f"Пропуск сервера с ID: {element['id']}",
                        lg.level.debug,
                    )
                    continue
                result.append(servers[server]["id"])
            return result
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return None

    def assure_community_ownership(self, group: int) -> bool:
        try:
            result = self.get_community_callback_servers(group=group)
            if result is None:
                return False
            return True
        except self.exception_tuple:
            return False

    def change_community_wall_state(self, group: int, state: bool):
        try:
            self.vk.groups.edit(group_id=group, wall=2 if state else 0)
            lg.log(
                f"Изменили статус стены у группы {group} на {state}",
                tp=lg.level.debug,
                name=self.name,
            )
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)

    def change_community_callback_editor_state(
        self, group: int, server: int, state: int
    ):
        try:
            self.vk.groups.setCallbackSettings(
                group_id=group, server_id=server, group_officers_edit=state
            )
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
        else:
            lg.log(
                f"Поменяли Callback у {group} на {state}, сервер: {server}",
                lg.level.debug,
            )

    def change_community_callback_banned_state(
        self, group: int, server: int, state: int
    ):
        try:
            self.vk.groups.setCallbackSettings(
                group_id=group, server_id=server, user_block=state, group_leave=state
            )
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
        else:
            lg.log(
                f"Поменяли Callback у {group} на {state}, сервер: {server}",
                lg.level.debug,
            )

    def change_community_callback_unbanned_state(
        self, group: int, server: int, state: int
    ):
        try:
            self.vk.groups.setCallbackSettings(
                group_id=group, server_id=server, user_unblock=state
            )
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
        else:
            lg.log(
                f"Поменяли Callback у {group} на {state}, сервер: {server}",
                lg.level.debug,
            )

    def change_community_callback_wall_states(
        self, group: int, server: int, state: int
    ):
        try:
            self.vk.groups.setCallbackSettings(
                group_id=group,
                server_id=server,
                wall_post_new=state,
                wall_repost=state,
                group_change_settings=state,
            )
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
        else:
            lg.log(
                f"Поменяли Callback у {group} на {state}, сервер: {server}",
                lg.level.debug,
            )

    @staticmethod
    def __remove_included_list(array: typing.List[list]) -> typing.List:
        ids = []
        for index, _ in enumerate(array):
            for second_index, _ in enumerate(array[index]):
                ids.append(array[index][second_index])
        return ids

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
            ids = self.__remove_included_list(banned_users)
            banned_users = ids
            for index, _ in enumerate(banned_users):
                banned_users[index] = banned_users[index]["profile"]["id"]
        except vk_api.exceptions.Captcha:
            sleep(10)
            return self.get_banned_members(group)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return None
        return banned_users

    def get_all_community_members(
        self, group: int, managers: bool = False, with_banned: bool = True
    ):
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
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return None

    def repost(self, group: int, message: str) -> bool:
        try:
            result = self.vk.wall.repost(group_id=group, object=message)
            if "success" in result and result["success"] == 1:
                return True
            return False
        except vk_api.exceptions.Captcha as capt:
            self.captcha_handler(capt)
            return True
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            return False

    def block(
        self, group: int, ban_list: typing.List[int], com: str, debug: bool = False
    ):
        banned_users = self.get_banned_members(group)
        ban_list = [i for i in ban_list if i not in banned_users]
        counter = 0
        while counter < len(ban_list):
            user = ban_list[counter]
            response = 0
            try:
                response = self.vk.groups.ban(
                    group_id=group,
                    owner_id=user,
                    comment=com if len(com) > 1 else None,
                    comment_visible=1,
                )
            except vk_api.exceptions.Captcha as capt:
                if self.saves.captcha_ban:
                    try:
                        self.captcha_handler(capt)
                    except self.exception_tuple:
                        pass
                    response = 1
                else:
                    lg.log("Пауза на 35 секунд", lg.level.debug, self.name)
                    response = -1
                    counter -= 1
                    sleep(35)
            except self.exception_tuple as Error:
                lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            if response == 1:
                lg.log(
                    f"ID {user} добавлен в чёрный список сообщества {group}",
                    tp=lg.level.debug if debug else lg.level.success,
                    name=self.name,
                )
            elif response != -1:
                lg.log(
                    f"ID {user} не добавлен в чёрный список сообщества {group}",
                    lg.level.warn,
                    self.name,
                )
            counter += 1

    def unblock(self, group: int, ban_list: typing.List[int], captcha: bool = True):
        for user in ban_list:
            response = 0
            try:
                response = self.vk.groups.unban(group_id=group, owner_id=user)
            except vk_api.exceptions.Captcha as capt:
                if captcha:
                    self.captcha_handler(capt)
                else:
                    lg.log("Пауза на 15 секунд", 5, self.name)
                    sleep(15)
                response = -1
            except self.exception_tuple as Error:
                lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            if response == 1:
                lg.log(
                    f"ID {user} убран из чёрного списка сообщества {group}",
                    name=self.name,
                )
            elif response != -1:
                lg.log(
                    f"Не удалось убрать ID {user} из чёрного списка сообщества {group}",
                    2,
                    self.name,
                )

    def editor(
        self,
        group: int,
        users: typing.List[int],
        limit: int = 100,
        clear: bool = False,
        debug: bool = False,
    ):
        task_sleep = 7200
        counter = managers_count = 0
        if limit == 0:
            return
        while True:
            if counter >= len(users):
                return
            if managers_count >= limit:
                lg.log(
                    f"Достигнут лимит руководителей ({limit})",
                    lg.level.debug,
                    name=self.name,
                )
                return
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
                if not self.saves.captcha_editor:
                    lg.log(f"Пауза на {task_sleep} секунд", name=self.name)
                    counter -= 1
                    response = -1
                    sleep(task_sleep)
                else:
                    self.captcha_handler(capt)
                    response = -1
            except self.exception_tuple as Error:
                lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
            if response == 1:
                lg.log(
                    f"ID {user} {'убран из руководителей' if clear else 'добавлен в руководители'} сообщества {group}",
                    name=self.name,
                    tp=lg.level.debug if debug else lg.level.success,
                )
                managers_count += 1
            elif response != -1:
                lg.log(
                    f"Не удалось {'убрать из руководителей' if clear else 'добавить в руководители'} ID {user} "
                    f"сообщества {group}",
                    name=self.name,
                    tp=lg.level.debug if debug else lg.level.success,
                )
            counter += 1

    def ban_check(self, group: int, ban_list: typing.List[int]):
        try:
            managers = self.get_all_community_members(
                group=group,
                managers=True,
                with_banned=False,
            )
            if managers is None:
                return None
            banned = [i for i in managers if i in ban_list]
            return banned
        except vk_api.exceptions.Captcha:
            sleep(15)
            return self.ban_check(group, ban_list)
        except self.exception_tuple as Error:
            lg.log(f"Произошла ошибка: {Error}", tp=lg.level.error, name=self.name)
