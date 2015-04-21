from datetime import datetime, timedelta

import pytest

from kii import exceptions as exc, results as rs

from .conf import get_env, get_api, clean_up_of_user as cleanup


class TestUsersResult:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        cleanup()

    def test_result(self):
        api = get_api()
        env = get_env()
        test_user = env['test_user']

        with pytest.raises(exc.KiiPasswordTooShortError):
            user = api.user.create_a_user()

        with pytest.raises(exc.KiiInvalidInputDataError):
            user = api.user.create_a_user(password=test_user['password'])

        user = api.user.create_a_user(login_name=test_user['login_name'],
                                      password=test_user['password'])

        assert isinstance(user, rs.UserResult)

        # disabled
        assert isinstance(user._disabled, bool)
        assert user._disabled is False

        # has password
        assert isinstance(user._has_password, bool)
        assert user._has_password is True
        assert isinstance(user._hasPassword, bool)
        assert user._hasPassword is True

        # internal user id
        assert isinstance(user.internal_user_id, int)
        assert isinstance(user.internalUserID, int)

        # login name
        assert isinstance(user.login_name, str)
        assert isinstance(user.loginName, str)

        # user id
        assert isinstance(user.user_id, str)
        assert isinstance(user.userID, str)


class TestUsers:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        cleanup()

    def test_create_user(self):
        api = get_api()
        env = get_env()
        test_user = env['test_user']

        with pytest.raises(exc.KiiPasswordTooShortError):
            api.user.create_a_user()

        with pytest.raises(exc.KiiInvalidInputDataError):
            api.user.create_a_user(password=test_user['password'])

        user = api.user.create_a_user(login_name=test_user['login_name'],
                                      password=test_user['password'])
        assert user

        with pytest.raises(exc.KiiUserAlreadyExistsError):
            api.user.create_a_user(login_name=test_user['login_name'],
                                   password=test_user['password'])

    def test_create_user2(self):
        api = get_api()
        env = get_env()
        test_user = env['test_user']

        user = api.user.create_a_user(login_name=test_user['login_name'],
                                      password=test_user['password'])

        with pytest.raises(exc.KiiHasNotPropertyError):
            user.country

        cleanup()

        user = api.user.create_a_user(login_name=test_user['login_name'],
                                      password=test_user['password'],
                                      country='jp')

        assert user.country == 'JP'

    def test_create_user_and_obtain_access_token(self):
        api = get_api()
        env = get_env()
        test_user = env['test_user']

        user = api.user.create_a_user_and_obtain_access_token(login_name=test_user['login_name'],
                                                              password=test_user['password'])

        assert isinstance(user._access_token, str)

    def test_delete_user(self):
        api = get_api()
        env = get_env()
        test_user = env['test_user']

        user = api.user.create_a_user(login_name=test_user['login_name'],
                                      password=test_user['password'])

        with pytest.raises(exc.KiiUserHasNotAccessTokenError):
            user.delete()

        cleanup()

        user = api.user.create_a_user_and_obtain_access_token(login_name=test_user['login_name'],
                                                              password=test_user['password'])

        user.delete()

        with pytest.raises(exc.KiiWrongTokenError):
            user.delete()

    def test_login_user(self):
        api = get_api()
        env = get_env()
        test_user = env['test_user']

        user = api.user.create_a_user_and_obtain_access_token(login_name=test_user['login_name'],
                                                              password=test_user['password'])

        old_token = user.access_token

        new_token = api.user.login(test_user['login_name'], test_user['password'])

        assert old_token != new_token.access_token
        # do not specify
        assert new_token.expires_in > 1000000

        # specify
        EXPIRE_SEC = 5
        expire = datetime.now() + timedelta(seconds=EXPIRE_SEC)
        new_token2 = api.user.login(test_user['login_name'],
                                    test_user['password'],
                                    expires_at=expire)

        assert new_token2.expires_in < (EXPIRE_SEC + 1)
