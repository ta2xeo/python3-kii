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


class TestApplicationScopeData:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        self.scope = self.api.data.application

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(BUCKET_ID)
        except exc.KiiBucketNotFoundError:
            pass
        cleanup()

    def test_retrieve_bucket(self):
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

    def test_create_an_object(self):
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

    def test_retrieve_an_object(self):
        obj = self.scope(BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        result = self.scope(BUCKET_ID).retrieve_an_object(obj.object_id)

        assert isinstance(result, rs.ObjectResult)
        assert result._id
        assert isinstance(result._id, str)
        assert result._created
        assert result._modified

    def test_fully_update_an_object(self):
        bucket = self.scope(BUCKET_ID)
        obj = bucket.create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 1

        created = bucket.retrieve_an_object(obj.object_id)

        assert created['int key'] == 1
        assert created['str key'] == 'this is string'
        assert created['dict key'] == {
            'nest': 'nest value',
        }
        assert created['list key'] == [1, 2, 3]

        updated = bucket.fully_update_an_object(obj.object_id, {
            'str key': 'updated string',
            'dict key': {
                'nest': {
                    'nest2': 'nest and nest',
                },
            },
            'list key': [4, 5, 6],
        })

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 1

        updated = bucket.retrieve_an_object(obj.object_id)

        assert 'int key' not in updated
        assert updated['str key'] == 'updated string'
        assert updated['dict key'] == {
            'nest': {
                'nest2': 'nest and nest',
            }
        }
        assert updated['list key'] == [4, 5, 6]

        assert created._created == updated._created
        assert created._modified != updated._modified
        assert created._version != updated._version

    def test_create_a_new_object_with_an_id(self):
        bucket = self.scope(BUCKET_ID)
        obj = bucket.create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })
        created = bucket.retrieve_an_object(obj.object_id)

        assert created['int key'] == 1
        assert created['str key'] == 'this is string'
        assert created['dict key'] == {
            'nest': 'nest value',
        }
        assert created['list key'] == [1, 2, 3]

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 1

        created2 = bucket.create_a_new_object_with_an_id('new-object-id', {
            'str key': 'created2 string',
            'dict key': {
                'nest': {
                    'nest2': 'nest and nest',
                },
            },
            'list key': [4, 5, 6],
        })

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 2

        created2 = bucket.retrieve_an_object('new-object-id')

        assert 'int key' not in created2
        assert created2['str key'] == 'created2 string'
        assert created2['dict key'] == {
            'nest': {
                'nest2': 'nest and nest',
            }
        }
        assert created2['list key'] == [4, 5, 6]

        assert created._created != created2._created
        assert created._modified != created2._modified
        assert created._version == 1
        assert created2._version == 1

    def test_partially_update_an_object(self):
        bucket = self.scope(BUCKET_ID)
        obj = bucket.create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 1

        created = bucket.retrieve_an_object(obj.object_id)

        assert created['int key'] == 1
        assert created['str key'] == 'this is string'
        assert created['dict key'] == {
            'nest': 'nest value',
        }
        assert created['list key'] == [1, 2, 3]

        updated = bucket.partially_update_an_object(obj.object_id, {
            'str key': 'updated string',
            'dict key': {
                'nest': {
                    'nest2': 'nest and nest',
                },
            },
        })

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 1

        updated = bucket.retrieve_an_object(obj.object_id)

        assert 'int key' in updated
        assert updated['int key'] == 1
        assert updated['str key'] == 'updated string'
        assert updated['dict key'] == {
            'nest': {
                'nest2': 'nest and nest',
            }
        }
        assert 'list key' in updated
        assert updated['list key'] == [1, 2, 3]

        assert created._created == updated._created
        assert created._modified != updated._modified
        assert created._version == 1
        assert updated._version == 2

    def test_delete_an_object(self):
        bucket = self.scope(BUCKET_ID)
        obj = bucket.create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 1

        created = bucket.retrieve_an_object(obj.object_id)

        assert created['int key'] == 1
        assert created['str key'] == 'this is string'
        assert created['dict key'] == {
            'nest': 'nest value',
        }
        assert created['list key'] == [1, 2, 3]

        bucket.delete_an_object(obj.object_id)

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 0

        with pytest.raises(exc.KiiObjectNotFoundError):
            obj = bucket.retrieve_an_object(obj.object_id)

    def test_query_for_objects(self):
        bucket = self.scope(BUCKET_ID)
        OBJ_COUNT = 10
        for i in range(OBJ_COUNT):
            even = i % 2 == 0
            bucket.create_an_object({
                'index': i,
                'desc': 'An object number is {0}.'.format(i + 1),
                'name': 'test user',
                'even': even,
            })

        # all
        results = bucket.query_for_objects()
        assert len(results) == OBJ_COUNT

        # equal
        results = bucket.query_for_objects(cl.Clause.eq('index', 3))
        assert len(results) == 1
        assert results[0]['index'] == 3
        assert results[0]['desc'] == 'An object number is 4.'

        # not
        results = bucket.query_for_objects(cl.Clause.not_(cl.Clause.eq('index', 2)))
        assert len(results) == OBJ_COUNT - 1
        for r in results:
            assert r['index'] != 2

        # prefix
        results = bucket.query_for_objects(cl.Clause.prefix('name', 'tes'))
        assert len(results) == OBJ_COUNT

        # range
        results = bucket.query_for_objects(cl.RangeClause('index').le(2))
        assert len(results) == 3

        results = bucket.query_for_objects(cl.RangeClause('index').lt(2))
        assert len(results) == 2

        results = bucket.query_for_objects(cl.RangeClause('index').ge(2))
        assert len(results) == OBJ_COUNT - 2

        results = bucket.query_for_objects(cl.RangeClause('index').gt(2))
        assert len(results) == OBJ_COUNT - 3

        # in
        results = bucket.query_for_objects(cl.Clause.in_('index', [1, 3, 4]))
        assert len(results) == 3
        for r in results:
            assert r['index'] in [1, 3, 4]

        # has
        results = bucket.query_for_objects(cl.HasFieldClause('index', 'INTEGER'))
        assert len(results) == OBJ_COUNT

        results = bucket.query_for_objects(cl.HasFieldClause('index', 'STRING'))
        assert len(results) == 0

        results = bucket.query_for_objects(
            cl.HasFieldClause('index', cl.HasFieldClause.Types.integer))
        assert len(results) == OBJ_COUNT

        results = bucket.query_for_objects(
            cl.HasFieldClause('index', cl.HasFieldClause.Types.string))
        assert len(results) == 0

        # and
        results = bucket.query_for_objects(
            cl.AndClause(
                cl.Clause.eq('even', True),
                cl.RangeClause('index').le(6)
            )
        )
        assert len(results) == 6 // 2 + 1

        # or
        results = bucket.query_for_objects(
            cl.OrClause(
                cl.Clause.eq('even', True),
                cl.RangeClause('index').le(6)
            )
        )
        assert len(results) == 6 + (OBJ_COUNT - 6) // 2

        # order_by, descending
        results = bucket.query_for_objects(order_by='index', descending=True)
        for i, r in enumerate(results):
            assert r['index'] == OBJ_COUNT - i - 1

        results = bucket.query_for_objects(order_by='index', descending=False)
        for i, r in enumerate(results):
            assert r['index'] == i

        # limit
        results = bucket.query_for_objects(limit=2)
        assert len(results) == 2

        results = bucket.query_for_objects(limit=4)
        assert len(results) == 4

        results = bucket.query_for_objects(limit=OBJ_COUNT + 20)
        assert len(results) == OBJ_COUNT

    def test_query_for_objects_pagination_key(self):
        bucket = self.scope(BUCKET_ID)
        OBJ_COUNT = 20
        for i in range(OBJ_COUNT):
            even = i % 2 == 0
            bucket.create_an_object({
                'index': i,
                'desc': 'An object number is {0}.'.format(i + 1),
                'name': 'test user',
                'even': even,
            })

        # pagination_key
        results = bucket.query_for_objects(limit=3)
        assert len(results) == 3

        results = bucket.query_for_objects(limit=3,
                                           pagination_key=results.next_pagination_key)
        assert len(results) == 3

        results = bucket.query_for_objects(pagination_key=results.next_pagination_key)
        assert len(results) == OBJ_COUNT - 6

        assert results.next_pagination_key is None

    def test_query_for_objects_huge(self):
        bucket = self.scope(BUCKET_ID)
        OBJ_COUNT = 410
        for i in range(OBJ_COUNT):
            even = i % 2 == 0
            bucket.create_an_object({
                'index': i,
                'desc': 'An object number is {0}.'.format(i + 1),
                'name': 'test user',
                'even': even,
            })

        # pagination_key
        results = bucket.query_for_objects()
        assert len(results) == OBJ_COUNT
