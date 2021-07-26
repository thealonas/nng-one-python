# -*- coding: utf-8 -*-
import sentry_sdk


class Sentry:
    sdk = sentry_sdk
    client = None

    @staticmethod
    def __cut_sensitive_data(event, hint):
        sensitive = ["token", "groups", "group", "data", "messages", "com", "owner_id"]
        frames = event["exception"]["values"][0]["stacktrace"]["frames"]
        for data in sensitive:
            for index, _ in enumerate(frames):
                if "vars" in frames[index] and data in frames[index]["vars"]:
                    print(frames[index]["vars"][data])
                    frames[index]["vars"][data] = "DATA REDACTED"
        event["exception"]["values"][0]["stacktrace"]["frames"] = frames
        return event

    def init(self):
        """
        Инициализация Sentry.
        Возвращает клиент, с которым скрипт может начинать работу.
        """
        self.client = self.sdk.Hub(
            self.sdk.Client(
                "https://f39baabe1083493e917977a30d573148@o555933.ingest.sentry.io/5686183",
                traces_sample_rate=1.0,
                ignore_errors=[KeyboardInterrupt],
                server_name=False,
                environment="production",
                release="nng-one@2.0",
                before_send=self.__cut_sensitive_data,
            )
        )
        return self.client
