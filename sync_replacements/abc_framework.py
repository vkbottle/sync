from abc import ABC, abstractmethod
from typing import NoReturn

from vkbottle_sync.api import ABCAPI
from vkbottle_sync.polling import ABCPolling


class ABCFramework(ABC):
    api: ABCAPI

    @property
    @abstractmethod
    def polling(self) -> ABCPolling:
        pass

    @abstractmethod
    def run_polling(self) -> NoReturn:
        pass

    @abstractmethod
    def run_forever(self) -> NoReturn:
        pass
