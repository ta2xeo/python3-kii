from datetime import datetime, timedelta

import pytest

from kii.exceptions import *
from kii.results import *

from conf import get_env, get_api, cleanup, get_test_user, get_admin_api


TEST_GROUP_NAME = 'test_group'


class TestGroups:
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

    def test_create_group_failed(self):
        api = get_api()
        env = get_env()

        with pytest.raises(KiiHasNotAccessTokenError):
            new_group = api.groups.create_a_group(TEST_GROUP_NAME, 'dummy')

        user = get_test_user()
        with pytest.raises(KiiUserNotFoundError):
            new_group = api.with_access_token(user.access_token).groups.create_a_group(TEST_GROUP_NAME, '_not_exists_user')

    def test_create_group(self):
        api = get_api()
        env = get_env()

        user = get_test_user()
        new_group = api.with_access_token(user.access_token).groups.create_a_group(TEST_GROUP_NAME, user.user_id)

        group = api.groups.delete_a_group(new_group.group_id)

    def test_delete_group(self):
        api = get_api()
        env = get_env()

        user = get_test_user()
        new_group = api.with_access_token(user.access_token).groups.create_a_group(TEST_GROUP_NAME, user.user_id)

        group = api.groups.delete_a_group(new_group.group_id)

        with pytest.raises(KiiGroupNotFoundError):
            api.groups.delete_a_group('unknown group id')
