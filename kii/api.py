# only python3.4 or later
from datetime import datetime
import warnings

from kii import exceptions as exc, results as rs
from kii.acl import AclManagement
from kii.data import DataManagement
from kii.enums import Site
from kii.groups import GroupManagement
from kii.users import RequestANewToken, UserManagement


warnings.simplefilter('always')


KII_REST_API_BASE_URL = 'https://api{domain}.kii.com/api'
DEFAULT_REGION = Site.US


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

        self.user = UserManagement(self)
        self.group = GroupManagement(self)
        self.data = DataManagement(self)

        self.acl = AclManagement(self)

    @property
    def users(self):
        warnings.warn('users property deprecates in the near future. Use user property.',
                      PendingDeprecationWarning)
        return self.user

    @property
    def groups(self):
        warnings.warn('groups property deprecates in the near future. Use group property.',
                      PendingDeprecationWarning)
        return self.group

    @property
    def buckets(self):
        warnings.warn('buckets property deprecates in the near future. Use data property.',
                      PendingDeprecationWarning)
        return self.data

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, token):
        if isinstance(token, rs.TokenResult):
            self._access_token = token.access_token
            self.token_type = token.token_type
        else:
            self._access_token = token

    @property
    def endpoint_url(self):
        return KII_REST_API_BASE_URL.format(domain=self.region.value)

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, site):
        if not isinstance(site, Site):
            warnings.warn('deprecated string code. Use Site enum object.',
                          PendingDeprecationWarning)
            site = Site[site.upper()]
        self._region = site

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
        if expires_at and not isinstance(expires_at, datetime):
            raise exc.KiiInvalidExpirationError

        req = RequestANewToken(self,
                               expires_at=expires_at,
                               client_id=self.client_id,
                               client_secret=self.client_secret)
        return req.request()
