# only python3.4 or later
from datetime import (
    datetime,
    timedelta,
)

from kii.buckets import Buckets
from kii.exceptions import *
from kii.groups import Groups
from kii.helpers import *
from kii.users import (
    RequestANewToken,
    Users,
)


KII_REST_API_BASE_URL = 'https://api{domain}.kii.com/api'

DOMAINS = {
    'US': '',
    'JP': '-jp',
}

DEFAULT_REGION = 'US'


class KiiAPI:
    def __init__(self,
                 app_id,
                 app_key,
                 *,
                 token_type=None,
                 access_token=None,
                 region=DEFAULT_REGION):
        self.app_id = app_id
        self.app_key = app_key
        self.token_type = token_type
        self.access_token = access_token
        self.region = region

        self.users = Users(self)
        self.groups = Groups(self)
        self.buckets = Buckets(self)

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, token):
        if isinstance(token, TokenResult):
            self._access_token = token.access_token
            self.token_type = token.token_type
        else:
            self._access_token = token

    def with_access_token(self, access_token, token_type=None):
        '''
        An access token is preserved on KiiAPI class.
        '''
        self.access_token = access_token
        if self.token_type is not None:
            self.token_type = token_type
        return self

    def clone(self, **kwargs):
        base = {
            'token_type': self.token_type,
            'access_token': self.access_token,
            'region': self.region,
        }
        base.update(kwargs)
        return KiiAPI(self.app_id, self.app_key, **base)

    @property
    def endpoint_url(self):
        return KII_REST_API_BASE_URL.format(domain=DOMAINS[self.region.upper()])


class KiiAdminAPI(KiiAPI):
    def __init__(self,
                 app_id,
                 app_key,
                 client_id,
                 client_secret,
                 expires_at=None,
                 **kwargs):
        """
        expires_at: The date in Unix epoch in milliseconds
                    when the admin access token should expire
        """
        super().__init__(app_id, app_key, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

        if self.access_token is None:
            token = self.get_admin_token(expires_at)
            self.token_type = token.token_type
            self.access_token = token.access_token

    def clone(self, **kwargs):
        base = {
            'token_type': self.token_type,
            'access_token': self.access_token,
            'region': self.region,
        }
        base.update(kwargs)
        return KiiAdminAPI(self.app_id, self.app_key,
                           self.client_id, self.client_secret, **base)

    def get_admin_token(self, expires_at=None):
        if expires_at and not isinstanceis(expires_at, datetime):
            raise KiiInvalidExpirationError

        req = RequestANewToken(self,
                               expires_at=expires_at,
                               client_id=self.client_id,
                               client_secret=self.client_secret)
        return req.request()


class JPKiiAPI(KiiAPI):
    def __init__(self, *args, **kwargs):
        if 'region' in kwargs:
            del kwargs['region']
        super().__init__(*args, region='JP', **kwargs)
