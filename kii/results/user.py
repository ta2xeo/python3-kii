from .base import BaseResult
from kii.exceptions import (
    KiiHasNotPropertyError,
    KiiUserHasNotAccessTokenError,
)


class UserResult(BaseResult):
    @property
    def _access_token(self):
        try:
            return self._result['_accessToken']
        except KeyError as e:
            raise KiiUserHasNotAccessTokenError from e

    @property
    def _accessToken(self):
        """
        synonym
        """
        return self._access_token

    @property
    def _disabled(self):
        return self._result['_disabled']

    @property
    def _has_password(self):
        return self._result['_hasPassword']

    @property
    def _hasPassword(self):
        """
        synonym
        """
        return self._has_password

    @property
    def access_token(self):
        return self._access_token

    @property
    def country(self):
        try:
            return self._result['country']
        except KeyError as e:
            raise KiiHasNotPropertyError('this user has not country property') from e

    @property
    def display_name(self):
        return self._result['displayName']

    @property
    def displayName(self):
        """
        synonym
        """
        return self.display_name

    @property
    def email_address(self):
        return self._result['emailAddress']

    @property
    def emailAddress(self):
        """
        synonym
        """
        return self.email_address

    @property
    def email_address_verified(self):
        return self._result['emailAddressVerified']

    @property
    def emailAddressVerified(self):
        """
        synonym
        """
        return self.email_address_verified

    @property
    def internal_user_id(self):
        return self._result['internalUserID']

    @property
    def internalUserID(self):
        """
        synonym
        """
        return self.internal_user_id

    @property
    def locale(self):
        return self._result['locale']

    @property
    def login_name(self):
        return self._result['loginName']

    @property
    def loginName(self):
        """
        synonym
        """
        return self.login_name

    @property
    def phone_number(self):
        return self._result['phoneNumber']

    @property
    def phoneNumber(self):
        """
        synonym
        """
        return self.phone_number

    @property
    def phone_number_verified(self):
        return self._result['phoneNumberVerified']

    @property
    def phoneNumberVerified(self):
        """
        synonym
        """
        return self.phone_number_verified

    @property
    def user_id(self):
        return self._result['userID']

    @property
    def userID(self):
        """
        synonym
        """
        return self.user_id

    def delete(self):
        api = self.api.clone(access_token=self.access_token)
        api.user.delete_a_user()
