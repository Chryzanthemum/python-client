import logging
from abc import ABC
from typing import Type

import requests
from pydantic import Field

from steamship.experimental.package_starters.web_bot import (
    SteamshipWidgetBot,
    response_for_exception,
)
from steamship.experimental.transports import TelegramTransport
from steamship.invocable import Config, InvocableResponse, post


class TelegramBotConfig(Config):
    bot_token: str = Field(description="The secret token for your Telegram bot")


class TelegramBot(SteamshipWidgetBot, ABC):
    config: TelegramBotConfig
    telegram_transport: TelegramTransport

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class."""
        return TelegramBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_root = f"https://api.telegram.org/bot{self.config.bot_token}"
        self.telegram_transport = TelegramTransport(
            bot_token=self.config.bot_token, client=self.client
        )  # dangerous!

    def instance_init(self):
        """This instance init method is called automatically when an instance of this package is created. It registers the URL of the instance as the Telegram webhook for messages."""
        super().instance_init()
        webhook_url = self.context.invocable_url + "respond"
        self.telegram_transport.instance_init(webhook_url=webhook_url)

    @post("respond", public=True)
    def respond(self, **kwargs) -> InvocableResponse[str]:
        """Endpoint implementing the Telegram WebHook contract. This is a PUBLIC endpoint since Telegram cannot pass a Bearer token."""

        # TODO: must reject things not from the package
        message = kwargs.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        try:
            incoming_message = self.telegram_transport.parse_inbound(message)
            if incoming_message is not None:
                response = self.create_response(incoming_message)
                if response is not None:
                    self.telegram_transport.send(response)
                else:
                    # Do nothing here; this could be a message we intentionally don't want to respond to (ex. an image or file upload)
                    pass
            else:
                # Do nothing here; this could be a message we intentionally don't want to respond to (ex. an image or file upload)
                pass
        except Exception as e:
            response = response_for_exception(e, chat_id=chat_id)

            if chat_id is not None:
                self.telegram_transport.send([response])
        # Even if we do nothing, make sure we return ok
        return InvocableResponse(string="OK")

    @post("webhook_info")
    def webhook_info(self) -> dict:
        return requests.get(self.api_root + "/getWebhookInfo").json()

    @post("info")
    def info(self) -> dict:
        """Endpoint returning information about this bot."""
        return self.telegram_transport.info()

    @post("disconnect_webhook")
    def disconnect_webhook(self) -> InvocableResponse[str]:
        self.telegram_transport.instance_deinit()
        logging.info("Disconnected webhook.")
        return InvocableResponse(data="OK")