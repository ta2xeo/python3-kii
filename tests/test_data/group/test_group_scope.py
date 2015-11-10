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


class TestGroupScopeBuckets:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        user = self.api.user.retrieve_user_data()
        self.scope = self.api.data.group
        self.group = self.api.group.create_a_group(GROUP_NAME, user.user_id)

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(self.group.group_id, BUCKET_ID)
        except exc.KiiBucketNotFoundError:
            pass
        cleanup()

    def test_create_object(self):
        obj = self.scope(self.group.group_id, BUCKET_ID).create_an_object({
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

    def test_retrieve_bucket(self):
        obj = self.scope(self.group.group_id, BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })
        assert obj

        bucket = self.scope.retrieve_a_bucket(self.group.group_id, BUCKET_ID)

        assert isinstance(bucket, rs.BucketResult)
        assert bucket.bucket_type is BucketType.READ_WRITE
        assert bucket.size > 0

    def test_delete_bucket(self):
        obj = self.scope(self.group.group_id, BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })
        assert obj

        self.scope.delete_a_bucket(self.group.group_id, BUCKET_ID)

        with pytest.raises(exc.KiiBucketNotFoundError):
            self.scope.delete_a_bucket(self.group.group_id, BUCKET_ID)
