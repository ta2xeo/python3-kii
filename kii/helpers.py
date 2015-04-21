import logging
import requests

from kii.exceptions import KiiAPIError, KiiHasNotAccessTokenError


logger = logging.getLogger(__name__)


class RequestHelper:
    def __init__(self, api):
        self.api = api

    @property
    def url(self):
        return '{endpoint_url}{api_path}'.format(endpoint_url=self.api.endpoint_url,
                                                 api_path=self.api_path)

    @property
    def headers(self):
        return {
            'X-Kii-AppID': self.api.app_id,
            'X-Kii-AppKey': self.api.app_key,
        }

    def request(self, **kwargs):
        logger.debug('METHOD:%s URL:%s HEADERS:%s KWARGS:%s',
                     self.method, self.url, self.headers, kwargs)
        response = requests.request(self.method,
                                    self.url,
                                    headers=self.headers,
                                    **kwargs)

        logger.info('%s %s %d', self.method, self.url, response.status_code)

        if response.status_code >= 400:
            raise KiiAPIError.distribute_error(response)

        result = self.result_container(self, response)
        return result

    @property
    def token_type(self):
        return self.api.token_type

    @property
    def access_token(self):
        return self.api.access_token

    @property
    def authorization(self):
        if self.access_token is None:
            raise KiiHasNotAccessTokenError

        return '{token_type} {access_token}'.format(
            token_type=self.token_type or 'Bearer',
            access_token=self.access_token,
        )

    def clone(self):
        return self.__class__(self.api)


class AuthRequestHelper(RequestHelper):
    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Authorization': self.authorization,
        })
        return headers


class BucketsHelper(RequestHelper):
    def __init__(self, scope):
        self.scope = scope
        super().__init__(scope.api)

    @property
    def access_token(self):
        return self.api.access_token

    @property
    def api(self):
        return self.scope.api

    @api.setter
    def api(self, api):
        self.scope.api = api

    @property
    def bucket_id(self):
        return self.scope.bucket_id

    @property
    def token_type(self):
        return self.api.token_type

    def clone(self):
        return self.__class__(self.scope)
