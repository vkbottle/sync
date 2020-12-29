import typing

from requests import Session

from vkbottle_sync.modules import json as json_module
from vkbottle_sync.http.client.abc import ABCHTTPClient

if typing.TYPE_CHECKING:
    from vkbottle.http.middleware.abc import ABCHTTPMiddleware


class RequestsClient(ABCHTTPClient):
    def __init__(
        self,
        session: typing.Optional[Session] = None,
        middleware: typing.Optional["ABCHTTPMiddleware"] = None,
        json_processing_module: typing.Optional[typing.Any] = None,
    ):
        super().__init__()
        self.json_processing_module = json_processing_module or json_module

        self.session = session or Session()

        if middleware is not None:
            self.middleware = middleware

    def request_json(
        self, method: str, url: str, data: typing.Optional[dict] = None, **kwargs
    ) -> dict:
        with self.session.request(method, url, data=data, **kwargs) as response:
            return response.json()

    def request_text(
        self, method: str, url: str, data: typing.Optional[dict] = None, **kwargs
    ) -> str:
        with self.session.request(method, url, data=data, **kwargs) as response:
            return response.text

    def request_content(
        self, method: str, url: str, data: typing.Optional[dict] = None, **kwargs
    ) -> bytes:
        with self.session.request(method, url, data=data, **kwargs) as response:
            return response.content

    def close(self) -> typing.NoReturn:
        self.session.close()
