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


class TestUserScopeBuckets:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        self.scope = self.api.data.user

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(BUCKET_ID)
        except exc.KiiBucketNotFoundError:
            pass
        # cleanup()

    def test_retrieve_bucket_by_me(self):
        obj = self.scope(BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })
        assert obj

        bucket = self.scope.retrieve_a_bucket(BUCKET_ID)

        assert isinstance(bucket, rs.BucketResult)
        assert bucket.bucket_type is BucketType.READ_WRITE
        assert bucket.size > 0

    def test_retrieve_bucket_by_address(self):
        test_user = get_env()['test_user']
        obj = self.scope(
            BUCKET_ID,
            account_type='EMAIL',
            address=test_user['email']
        ).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })
        assert obj

        bucket = self.scope.retrieve_a_bucket(BUCKET_ID,
                                              account_type='EMAIL',
                                              address=test_user['email'])

        assert isinstance(bucket, rs.BucketResult)
        assert bucket.bucket_type is BucketType.READ_WRITE
        assert bucket.size > 0

        bucket2 = self.scope.retrieve_a_bucket(BUCKET_ID,
                                               account_type=AccountType.email,
                                               address=test_user['email'])

        assert isinstance(bucket2, rs.BucketResult)
        assert bucket2.bucket_type is BucketType.READ_WRITE
        assert bucket2.size > 0

        bucket3 = self.scope.retrieve_a_bucket(BUCKET_ID,
                                               account_type='PHONE',
                                               address=test_user['phone'])

        assert isinstance(bucket3, rs.BucketResult)
        assert bucket3.bucket_type is BucketType.READ_WRITE
        assert bucket3.size > 0

        bucket4 = self.scope.retrieve_a_bucket(BUCKET_ID,
                                               account_type=AccountType.phone,
                                               address=test_user['phone'])

        assert isinstance(bucket4, rs.BucketResult)
        assert bucket4.bucket_type is BucketType.READ_WRITE
        assert bucket4.size > 0

    def test_retrieve_bucket_by_id(self):
        test_user = self.api.user.retrieve_user_data()
        obj = self.scope(BUCKET_ID, user_id=test_user.user_id).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })
        assert obj

        bucket = self.scope.retrieve_a_bucket(BUCKET_ID, user_id=test_user.user_id)

        assert isinstance(bucket, rs.BucketResult)
        assert bucket.bucket_type is BucketType.READ_WRITE
        assert bucket.size > 0

    def test_delete_bucket(self):
        obj = self.scope(BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })
        assert obj

        self.scope.delete_a_bucket(BUCKET_ID)

        with pytest.raises(exc.KiiBucketNotFoundError):
            self.scope.delete_a_bucket(BUCKET_ID)

    def test_create_object_by_me(self):
        obj = self.scope(BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        assert isinstance(obj, rs.CreateResult)
        assert obj.object_id
        assert obj.created_at
        assert isinstance(obj.created_at, datetime)
        assert obj.data_type
        assert obj.data_type == 'application/json'

    def test_create_object_by_address(self):
        test_user = get_env()['test_user']
        obj = self.scope(
            BUCKET_ID,
            account_type=AccountType.email,
            address=test_user['email']
        ).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        assert isinstance(obj, rs.CreateResult)
        assert obj.object_id
        assert obj.created_at
        assert isinstance(obj.created_at, datetime)
        assert obj.data_type
        assert obj.data_type == 'application/json'

    def test_create_object_by_id(self):
        test_user = self.api.user.retrieve_user_data()
        obj = self.scope(BUCKET_ID, user_id=test_user.user_id).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        assert isinstance(obj, rs.CreateResult)
        assert obj.object_id
        assert obj.created_at
        assert isinstance(obj.created_at, datetime)
        assert obj.data_type
        assert obj.data_type == 'application/json'
