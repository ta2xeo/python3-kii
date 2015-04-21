import pytest

from kii import exceptions as exc

from .conf import get_api, cleanup, get_test_user


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

        with pytest.raises(exc.KiiHasNotAccessTokenError):
            api.group.create_a_group(TEST_GROUP_NAME, 'dummy')

        user = get_test_user()
        with pytest.raises(exc.KiiUserNotFoundError):
            api.with_access_token(user.access_token) \
               .group.create_a_group(TEST_GROUP_NAME, '_not_exists_user')

    def test_create_group(self):
        api = get_api()

        user = get_test_user()
        new_group = api.with_access_token(user.access_token) \
                       .group.create_a_group(TEST_GROUP_NAME, user.user_id)

        api.group.delete_a_group(new_group.group_id)

    def test_delete_group(self):
        api = get_api()

        user = get_test_user()
        new_group = api.with_access_token(user.access_token) \
                       .group.create_a_group(TEST_GROUP_NAME, user.user_id)

        api.group.delete_a_group(new_group.group_id)

        with pytest.raises(exc.KiiGroupNotFoundError):
            api.group.delete_a_group('unknown group id')
