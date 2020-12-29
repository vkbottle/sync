from typing import Optional, NoReturn
from typing import Union

from vkbottle_sync.api import ABCAPI, API, Token
from vkbottle_sync.dispatch import ABCRouter, BotRouter, BuiltinStateDispenser
from vkbottle_sync.exception_factory import ABCErrorHandler, ErrorHandler
from vkbottle_sync.framework.abc import ABCFramework
from vkbottle_sync.modules import logger
from vkbottle_sync.polling import ABCPolling, BotPolling
from .labeler import ABCBotLabeler, BotLabeler


class Bot(ABCFramework):
    def __init__(
        self,
        token: Optional[Token] = None,
        api: Optional[ABCAPI] = None,
        polling: Optional[ABCPolling] = None,
        router: Optional["ABCRouter"] = None,
        labeler: Optional["ABCBotLabeler"] = None,
        error_handler: Optional["ABCErrorHandler"] = None,
        task_each_event: bool = False,
    ):
        self.api: Union[ABCAPI, API] = API(token) if token is not None else api  # type: ignore
        self.error_handler = error_handler or ErrorHandler()
        self.labeler = labeler or BotLabeler()
        self.state_dispenser = BuiltinStateDispenser()
        self._polling = polling or BotPolling(self.api)
        self._router = router or BotRouter()
        self.task_each_event = task_each_event

    @property
    def polling(self) -> "ABCPolling":
        return self._polling.construct(self.api, self.error_handler)

    @property
    def router(self) -> "ABCRouter":
        return self._router.construct(
            views=self.labeler.views(),
            state_dispenser=self.state_dispenser,
            error_handler=self.error_handler,
        )

    @router.setter
    def router(self, new_router: "ABCRouter"):
        self._router = new_router

    @property
    def on(self) -> "ABCBotLabeler":
        return self.labeler

    def run_polling(self, custom_polling: Optional[ABCPolling] = None) -> NoReturn:
        polling = custom_polling or self.polling
        logger.info(f"Starting polling for {polling.api!r}")

        for event in polling.listen():  # type: ignore
            logger.debug(f"New event was received: {event}")
            for update in event["updates"]:
                if not self.task_each_event:
                    self.router.route(update, polling.api)
                else:
                    self.loop.create_task(self.router.route(update, polling.api))

    def run_forever(self) -> NoReturn:
        self.run_polling()
