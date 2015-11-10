from .base import BaseResult


class BodyResult(BaseResult):
    def __init__(self, request_helper, response):
        self.request_helper = request_helper
        self.response = response
        self.set_result(response.content)

    def __str__(self):
        return self.body.decode('utf-8')

    @property
    def body(self):
        return self._result
