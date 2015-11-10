from .base import BaseResult


class TokenResult(BaseResult):
    @property
    def access_token(self):
        return self._result['access_token']

    @property
    def expires_in(self):
        return self._result['expires_in']

    @property
    def id(self):
        return self._result['id']

    @property
    def token_type(self):
        return self._result['token_type']
