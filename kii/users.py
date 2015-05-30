from datetime import datetime
from enum import Enum, unique

from kii import exceptions as exc, results as rs
from kii.enums import UserRequestType
from kii.helpers import RequestHelper


@unique
class AccountType(Enum):
    email = 'EMAIL'
    phone = 'PHONE'
    login_name = 'LOGIN_NAME'


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
                raise exc.KiiInvalidAccountTypeError(
                    'account type "{0}" is invalid'.format(account_type))

        self._account_type = account_type


class RequestTypeMixin(AccountTypeMixin):
    @property
    def request_type(self):
        return RequestTypeMixin.get_request_type(self.api,
                                                 self.account_type,
                                                 self.address,
                                                 self.user_id)

    @classmethod
    def get_request_type(cls, api, account_type, address, user_id):
        from kii.api import KiiAdminAPI

        if account_type and address:
            return UserRequestType.by_address

        elif user_id:
            return UserRequestType.by_id

        else:
            # http://documentation.kii.com/en/guides/rest/admin-features/
            if isinstance(api, KiiAdminAPI):
                raise exc.KiiIllegalAccessError

        return UserRequestType.by_me_literal


class UserRequestHelper(RequestHelper, RequestTypeMixin):
    method = 'GET'
    result_container = rs.BaseResult

    def __init__(self, api, *, account_type=None, address=None, user_id=None):
        super().__init__(api)
        self.account_type = account_type
        self.address = address
        self.user_id = user_id

    def format_args(self):
        def by_address():
            return {
                'appID': self.api.app_id,
                'accountType': self.account_type,
                'address': self.address,
            }

        def by_id():
            return {
                'appID': self.api.app_id,
                'userID': self.user_id,
            }

        def by_me_literal():
            return {
                'appID': self.api.app_id,
            }

        return {
            UserRequestType.by_address: by_address,
            UserRequestType.by_id: by_id,
            UserRequestType.by_me_literal: by_me_literal,
        }[self.request_type]()

    @property
    def api_path(self):
        return self.paths[self.request_type].format(**self.format_args())


class UserManagement:
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

    def get_the_verification_code(self, *, account_type=None, address=None, user_id=None):
        helper = GetTheVerificationCode(self.api,
                                        account_type=account_type,
                                        address=address,
                                        user_id=user_id)
        result = helper.request()
        return result

    def verify_the_email_address(self, verification_code, *, account_type=None, address=None, user_id=None):
        helper = VerifyTheEmailAddress(self.api,
                                       verification_code,
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
    result_container = rs.UserResult

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


class DeleteAUser(UserRequestHelper, RequestTypeMixin):
    method = 'DELETE'
    result_container = rs.BaseResult
    paths = {
        UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}',
        UserRequestType.by_id: '/apps/{appID}/users/{userID}',
        UserRequestType.by_me_literal: '/apps/{appID}/users/me',
    }

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Authorization': self.authorization,
        })
        return headers


class RetrieveUserData(DeleteAUser):
    method = 'GET'
    result_container = rs.UserResult


class GetTheVerificationCode(UserRequestHelper):
    method = 'GET'
    result_container = rs.VerificationCodeResult
    paths = {
        UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/email-address/verification-code',
        UserRequestType.by_id: '/apps/{appID}/users/{userID}/email-address/verification-code',
        UserRequestType.by_me_literal: '/apps/{appID}/users/me/email-address/verification-code',
    }

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Authorization': self.authorization,
        })
        return headers


class VerifyTheEmailAddress(UserRequestHelper):
    method = 'POST'
    paths = {
        UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/email-address/verify',
        UserRequestType.by_id: '/apps/{appID}/users/{userID}/email-address/verify',
        UserRequestType.by_me_literal: '/apps/{appID}/users/me/email-address/verify',
    }

    def __init__(self, api, verification_code, *, account_type=None, address=None, user_id=None):
        super().__init__(api,
                         account_type=account_type,
                         address=address,
                         user_id=user_id)
        self.verification_code = verification_code

    @property
    def headers(self):
        headers = super().headers
        headers.update({
            'Content-Type': 'application/vnd.kii.AddressVerificationRequest+json',
        })
        return headers

    def request(self):
        params = {
            'verificationCode': self.verification_code,
        }

        return super().request(json=params)


class RequestANewToken(RequestHelper):
    method = 'POST'
    result_container = rs.TokenResult

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
                raise exc.KiiInvalidExpirationError

            expire = int(self.expires_at.timestamp() * 1000)
            params['expiresAt'] = expire

        if self.client_id is not None:
            params['client_id'] = self.client_id

        if self.client_secret is not None:
            params['client_secret'] = self.client_secret

        return super().request(json=params)
