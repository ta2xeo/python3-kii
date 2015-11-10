'''
Precondition
    successfully pass a users test.
'''
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


class TestApplicationObjectBody:
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
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)
        obj = bucket.query().one()
        try:
            bucket.delete_an_object_body(obj._id)
        except exc.KiiObjectBodyNotFoundError:
            pass

    def test_retrieve_an_object_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(exc.KiiObjectBodyNotFoundError):
            bucket.retrieve_an_object_body(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        body_result = bucket.retrieve_an_object_body(obj._id)
        assert body_result.body == body.encode('utf-8')

    def test_add_or_replace_object_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

        body_result = bucket.retrieve_an_object_body(obj._id)
        assert body_result.body == body.encode('utf-8')

        body = '0123456789'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        body_result = bucket.retrieve_an_object_body(obj._id)
        assert body_result.body == body.encode('utf-8')

    def test_verify_object_body_existence(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(exc.KiiObjectBodyNotFoundError):
            result = bucket.verify_the_object_body_existence(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        verified = bucket.verify_the_object_body_existence(obj._id)
        assert verified._result == ''
        assert 200 <= verified.status_code <= 204  # probably expects 204. but actually 200

    def test_has_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        assert bucket.has_body(obj._id) is False

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        assert bucket.has_body(obj._id) is True

    def test_has_object_body_existence(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(exc.KiiObjectBodyNotFoundError):
            result = bucket.verify_the_object_body_existence(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        verified = bucket.verify_the_object_body_existence(obj._id)
        assert verified._result == ''
        assert 200 <= verified.status_code <= 204  # probably expects 204. but actually 200

    def test_delete_an_object_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        body_result = bucket.retrieve_an_object_body(obj._id)
        assert body_result.body == body.encode('utf-8')

        bucket.delete_an_object_body(obj._id)

        with pytest.raises(exc.KiiObjectBodyNotFoundError):
            body_result = bucket.retrieve_an_object_body(obj._id)

        with pytest.raises(exc.KiiObjectBodyNotFoundError):
            bucket.delete_an_object_body(obj._id)

    def test_publish_an_object_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')
        assert result

        # no expiration
        published = bucket.publish_an_object_body(obj._id)
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
        published = bucket.publish_an_object_body(obj._id, expires_at=expire)

        res = requests.get(published.url)
        assert res.status_code == 200
        assert res.text == body

        # wait
        time.sleep(5)

        res = requests.get(published.url)
        assert res.status_code == 410

        # expiration is 3 seconds ago. another pattern.
        published = bucket.publish_an_object_body(obj._id, expires_in=3)

        res = requests.get(published.url)
        assert res.status_code == 200
        assert res.text == body

        # wait
        time.sleep(5)

        res = requests.get(published.url)
        assert res.status_code == 410
