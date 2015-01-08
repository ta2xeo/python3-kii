from datetime import datetime
from enum import Enum

from kii.exceptions import (
    KiiIllegalAccessError,
    KiiInvalidAccountTypeError,
)
from kii.helpers import RequestHelper
from kii.results import *


class AccountType(Enum):
    email = 'EMAIL'
    phone = 'PHONE'


class AccountTypeMixin:
    @property
    def account_type(self):
        if self._account_type is None:
            return None
        return self._account_type.value

    @account_type.setter
    def account_type(self, account_type):
        if account_type and not isinstance(account_type, AccountType):
            try:
                account_type = AccountType(account_type)
            except ValueError:
                raise KiiInvalidAccountTypeError('account type "{0}" is invalid'.format(account_type))

        self._account_type = account_type


class Users:
    def __init__(self, api):
        self.api = api

    def create_a_user(self, **kwargs):
        helper = CreateAUser(self.api, **kwargs)
        result = helper.request()
        return result


    def create_a_user_and_obtain_access_token(self, **kwargs):
        helper = CreateAUserAndObtainAccessToken(self.api, **kwargs)
        result = helper.request()
        return result

    def delete_a_user(self, *, account_type=None, address=None, user_id=None):
        helper = DeleteAUser(self.api,
                             account_type=account_type,
                             address=address,
                             user_id=user_id)
        result = helper.request()
        return result

    def retrieve_user_data(self, *, account_type=None, address=None, user_id=None):
        helper = RetrieveUserData(self.api,
                                  account_type=account_type,
                                  address=address,
                                  user_id=user_id)
        result = helper.request()
        return result

    def login(self, username, password, **kwargs):
        return self.request_a_new_token(username=username, password=password, **kwargs)

    def request_a_new_token(self,
                            *,
                            username=None,
                            password=None,
                            expires_at=None,
                            client_id=None,
                            client_secret=None):
        helper = RequestANewToken(self.api,
                                  username=username,
                                  password=password,
                                  expires_at=expires_at,
                                  client_id=client_id,
                                  client_secret=client_secret)
        result = helper.request()
        return result


class CreateAUser(RequestHelper):
    method = 'POST'
    result_container = UserResult

    def __init__(self, api,
                 login_name=None,
                 display_name=None,
                 country=None,
                 locale=None,
                 email_address=None,
                 phone_number=None,
                 phone_number_verified=None,
                 password=None):

        super().__init__(api)

        self.login_name = login_name
        self.display_name = display_name
        self.country = country
        self.locale = locale
        self.email_address = email_address
        self.phone_number = phone_number
        self.phone_number_verified = phone_number_verified
        self.password = password

    @property
    def api_path(self):
        return '/apps/{appID}/users'.format(appID=self.api.app_id)

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Content-Type': 'application/vnd.kii.RegistrationRequest+json',
        })
        return headers

    def request(self):
        params = {}

        if self.login_name is not None:
            params['loginName'] = self.login_name

        if self.display_name is not None:
            params['displayName'] = self.display_name

        if self.country is not None:
            params['country'] = self.country.upper()

        if self.locale is not None:
            params['locale'] = self.locale

        if self.email_address is not None:
            params['emailAddress'] = self.email_address

        if self.phone_number is not None:
            params['phoneNumber'] = self.phone_number

        if self.phone_number_verified is not None:
            params['phoneNumberVerified'] = self.phone_number_verified

        if self.password is not None:
            params['password'] = self.password

        return super().request(json=params)


class CreateAUserAndObtainAccessToken(CreateAUser):
    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Content-Type': 'application/vnd.kii.RegistrationAndAuthorizationRequest+json',
        })
        return headers


class DeleteAUser(RequestHelper):
    method = 'DELETE'
    result_container = BaseResult

    def __init__(self, api, *, account_type=None, address=None, user_id=None):
        super().__init__(api)
        self.account_type = account_type
        self.address = address
        self.user_id = user_id

    @property
    def api_path(self):
        from kii.api import KiiAdminAPI

        if self.account_type and self.address:
            return '/apps/{appID}/users/{accountType}:{address}'.format(
                appID=self.api.app_id,
                accountType=self.account_type,
                address=self.address
            )
        elif self.user_id:
            return '/apps/{appID}/users/{userID}'.format(
                appID=self.api.app_id,
                userID=self.user_id
            )

        if isinstance(self.api, KiiAdminAPI):
            raise KiiIllegalAccessError

        return '/apps/{appID}/users/me'.format(appID=self.api.app_id)

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Authorization': self.authorization,
        })
        return headers


class RetrieveUserData(DeleteAUser):
    method = 'GET'
    result_container = UserResult


class RequestANewToken(RequestHelper):
    method = 'POST'
    result_container = TokenResult

    def __init__(self, api,
                 *,
                 username=None,
                 password=None,
                 expires_at=None,
                 client_id=None,
                 client_secret=None):
        """
        expires_at: The date in Unix epoch in milliseconds
                    when the access token should expire
        """

        super().__init__(api)

        self.username = username
        self.password = password
        self.expires_at = expires_at
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def api_path(self):
        return '/oauth2/token'

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Content-Type': 'application/vnd.kii.OauthTokenRequest+json',
        })
        return headers

    def request(self):
        params = {}

        if self.username is not None:
            params['username'] = self.username

        if self.password is not None:
            params['password'] = self.password

        if self.expires_at is not None:
            if not isinstance(self.expires_at, datetime):
                raise KiiInvalidExpirationError

            expire = int(self.expires_at.timestamp() * 1000)
            params['expiresAt'] = expire

        if self.client_id is not None:
            params['client_id'] = self.client_id

        if self.client_secret is not None:
            params['client_secret'] = self.client_secret

        return super().request(json=params)
