from datetime import datetime, timedelta
import time

import pytest
import requests

from kii import AccountType, exceptions as exc, results as rs
from kii.data import BucketType, clauses as cl

from tests.conf import (
    get_env,
    get_api_with_test_user,
    cleanup,
)


GROUP_NAME = 'test_group'
BUCKET_ID = 'test_bucket'


class TestUtilityMethods:
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        cleanup()
        cls.api = get_api_with_test_user()
        cls.scope = cls.api.data.application
        bucket = cls.scope(BUCKET_ID)
        cls.OBJ_COUNT = 1
        for i in range(cls.OBJ_COUNT):
            even = i % 2 == 0
            bucket.create_an_object({
                'index': i,
                'desc': 'An object number is {0}.'.format(i + 1),
                'name': 'test user',
                'even': even,
            })

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        try:
            cls.scope.delete_a_bucket(BUCKET_ID)
        except exc.KiiBucketNotFoundError:
            pass
        cleanup()

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)
        obj = bucket.query().one()
        try:
            bucket.delete_an_object_body(obj._id)
        except exc.KiiObjectBodyNotFoundError:
            pass

    def test_refresh(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        bucket.partially_update_an_object(obj._id, {'name': 'updated user name', 'new key': 123})

        updated = bucket.query().one()

        assert obj._modified != updated._modified
        assert obj._version != updated._version
        assert obj['name'] == 'test user'
        assert updated['name'] == 'updated user name'
        assert 'new key' not in obj
        assert updated['new key'] == 123

        obj.refresh()

        assert obj._modified == updated._modified
        assert obj._version == updated._version
        assert obj['name'] == 'updated user name'
        assert 'new key' in obj
        assert obj['new key'] == 123

    def test_partially_update(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        obj.partially_update({'name': 'updated user name', 'new key': 123})

        updated = bucket.query().one()

        assert obj._modified != updated._modified
        assert obj._version != updated._version
        assert updated['name'] == 'updated user name'
        assert updated['new key'] == 123
        assert obj._id == updated._id

    def test_retrieve_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

        result = obj.retrieve_body()

        assert result.body == body.encode('utf-8')

    def test_add_or_replace_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = obj.add_or_replace_body(body, 'text/plain')
        assert result

        added = bucket.retrieve_an_object_body(obj._id)

        assert added.body == body.encode('utf-8')

    def test_verify_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(exc.KiiObjectBodyNotFoundError):
            result = bucket.verify_the_object_body_existence(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        verified = obj.verify_body()
        assert verified._result == ''
        assert 200 <= verified.status_code <= 204  # probably expects 204. but actually 200

    def test_has_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        assert obj.has_body() is False

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        assert obj.has_body() is True

    def test_delete_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(exc.KiiObjectBodyNotFoundError):
            obj.delete_body()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        obj.delete_body()

    def test_publish_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        # no expiration
        published = obj.publish_body()
        res = requests.get(published.url)
        assert res.status_code == 200
        assert res.text == body

        # wait
        time.sleep(5)

        res = requests.get(published.url)
        assert res.status_code == 200
        assert res.text == body

        # expiration is 3 seconds ago
        expire = datetime.now() + timedelta(seconds=3)
        published = obj.publish_body(expires_at=expire)

        res = requests.get(published.url)
        assert res.status_code == 200
        assert res.text == body

        # wait
        time.sleep(5)

        res = requests.get(published.url)
        assert res.status_code == 410

        # expiration is 3 seconds ago. another pattern.
        published = obj.publish_body(expires_in=3)

        res = requests.get(published.url)
        assert res.status_code == 200
        assert res.text == body

        # wait
        time.sleep(5)

        res = requests.get(published.url)
        assert res.status_code == 410
