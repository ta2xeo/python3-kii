'''
Precondition
    successfully pass a users test.
'''
from datetime import datetime, timedelta
import time

import pytest
import requests

from kii import AccountType
from kii.buckets.clauses import *
from kii.exceptions import *
from kii.results import *

from conf import (
    get_env,
    get_api,
    get_api_with_test_user,
    get_test_user,
    cleanup,
    get_admin_api,
)


GROUP_NAME = 'test_group'
BUCKET_ID = 'test_bucket'


class TestApplicationScopeBuckets:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        self.scope = self.api.buckets.application

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(BUCKET_ID)
        except KiiBucketNotFoundError:
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

        bucket = self.scope.retrieve_a_bucket(BUCKET_ID)

        assert isinstance(bucket, BucketResult)
        assert bucket.bucket_type == 'READ_WRITE'
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
        self.scope.delete_a_bucket(BUCKET_ID)

        with pytest.raises(KiiBucketNotFoundError):
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

        assert isinstance(obj, CreateResult)
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

        assert isinstance(result, ObjectResult)
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


        deleted = bucket.delete_an_object(obj.object_id)

        info = self.scope.retrieve_a_bucket(BUCKET_ID)
        assert info.size == 0

        with pytest.raises(KiiObjectNotFoundError):
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
        results = bucket.query_for_objects(Clause.eq('index', 3))
        assert len(results) == 1
        assert results[0]['index'] == 3
        assert results[0]['desc'] == 'An object number is 4.'

        # not
        results = bucket.query_for_objects(Clause.not_(Clause.eq('index', 2)))
        assert len(results) == OBJ_COUNT - 1
        for r in results:
            assert r['index'] != 2

        # prefix
        results = bucket.query_for_objects(Clause.prefix('name', 'tes'))
        assert len(results) == OBJ_COUNT

        # range
        results = bucket.query_for_objects(RangeClause('index').le(2))
        assert len(results) == 3

        results = bucket.query_for_objects(RangeClause('index').lt(2))
        assert len(results) == 2

        results = bucket.query_for_objects(RangeClause('index').ge(2))
        assert len(results) == OBJ_COUNT - 2

        results = bucket.query_for_objects(RangeClause('index').gt(2))
        assert len(results) == OBJ_COUNT - 3

        # in
        results = bucket.query_for_objects(Clause.in_('index', [1, 3, 4]))
        assert len(results) == 3
        for r in results:
            assert r['index'] in [1, 3, 4]

        # has
        results = bucket.query_for_objects(HasFieldClause('index', 'INTEGER'))
        assert len(results) == OBJ_COUNT

        results = bucket.query_for_objects(HasFieldClause('index', 'STRING'))
        assert len(results) == 0

        results = bucket.query_for_objects(HasFieldClause('index', HasFieldClause.Types.integer))
        assert len(results) == OBJ_COUNT

        results = bucket.query_for_objects(HasFieldClause('index', HasFieldClause.Types.string))
        assert len(results) == 0

        # and
        results = bucket.query_for_objects(AndClause(Clause.eq('even', True), RangeClause('index').le(6)))
        assert len(results) == 6 // 2 + 1

        # or
        results = bucket.query_for_objects(OrClause(Clause.eq('even', True), RangeClause('index').le(6)))
        assert len(results) == 6 + (OBJ_COUNT - 6) // 2

        # order_by, descending
        results = bucket.query_for_objects(order_by='index', descending=True)
        for i, r in enumerate(results):
            assert r['index'] == OBJ_COUNT - i - 1

        results = bucket.query_for_objects(order_by='index', descending=False)
        for i, r in enumerate(results):
            assert r['index'] == i

        # best_effort_limit
        results = bucket.query_for_objects(best_effort_limit=2)
        assert len(results) == 2

        results = bucket.query_for_objects(best_effort_limit=4)
        assert len(results) == 4

        results = bucket.query_for_objects(best_effort_limit=OBJ_COUNT + 20)
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
        results = bucket.query_for_objects(best_effort_limit=3)
        assert len(results) == 3

        results = bucket.query_for_objects(best_effort_limit=3, pagination_key=results.next_pagination_key)
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


class TestApplicationQuery:
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        cleanup()
        cls.api = get_api_with_test_user()
        cls.scope = cls.api.buckets.application
        bucket = cls.scope(BUCKET_ID)
        cls.OBJ_COUNT = 20
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
        except KiiBucketNotFoundError:
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

    def test_query_all(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        # all
        results = bucket.query().all()
        assert len(results) == cls.OBJ_COUNT

        results = bucket.query(RangeClause('index').lt(4)).all()
        assert len(results) == 4

        results = bucket.query(
            RangeClause('index').lt(8),
            EqualClause('even', False),
        ).all()
        assert len(results) == 4

        results = bucket.query(EqualClause('index', -1)).all()
        assert len(results) == 0

    def test_query_one(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        # one
        result = bucket.query(EqualClause('index', 1)).one()
        assert isinstance(result, ObjectResult)
        assert result._created
        assert result._modified
        assert result._owner
        assert result._version == 1

        with pytest.raises(KiiMultipleResultsFoundError):
            bucket.query(EqualClause('name', 'test user')).one()

        with pytest.raises(KiiObjectNotFoundError):
            bucket.query(EqualClause('name', 'unknown')).one()

    def test_query_first(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        # first
        result = bucket.query(EqualClause('index', 1)).first()
        assert isinstance(result, ObjectResult)
        assert result._created
        assert result._modified
        assert result._owner
        assert result._version == 1

        result = bucket.query(EqualClause('index', -1)).first()
        assert result is None

    def test_query_limit(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        results = bucket.query().limit(3).all()
        assert len(results) == 3

        results = bucket.query().limit(3000).all()
        assert len(results) == cls.OBJ_COUNT

    def test_query_order_by(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        results = bucket.query().order_by('index').all()
        for i in range(cls.OBJ_COUNT):
            assert results[i]['index'] == cls.OBJ_COUNT - i - 1

        results = bucket.query().order_by('index', False).all()
        for i in range(cls.OBJ_COUNT):
            assert results[i]['index'] == i


class TestApplicationObjectBody:
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        cleanup()
        cls.api = get_api_with_test_user()
        cls.scope = cls.api.buckets.application
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
        except KiiBucketNotFoundError:
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
        except KiiObjectBodyNotFoundError:
            pass

    def test_retrieve_an_object_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(KiiObjectBodyNotFoundError):
            bucket.retrieve_an_object_body(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

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

        body_result = bucket.retrieve_an_object_body(obj._id)
        assert body_result.body == body.encode('utf-8')

    def test_verify_object_body_existence(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(KiiObjectBodyNotFoundError):
            result = bucket.verify_the_object_body_existence(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

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

        assert bucket.has_body(obj._id) is True

    def test_has_object_body_existence(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(KiiObjectBodyNotFoundError):
            result = bucket.verify_the_object_body_existence(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

        verified = bucket.verify_the_object_body_existence(obj._id)
        assert verified._result == ''
        assert 200 <= verified.status_code <= 204  # probably expects 204. but actually 200

    def test_delete_an_object_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

        body_result = bucket.retrieve_an_object_body(obj._id)
        assert body_result.body == body.encode('utf-8')

        deleted = bucket.delete_an_object_body(obj._id)

        with pytest.raises(KiiObjectBodyNotFoundError):
            body_result = bucket.retrieve_an_object_body(obj._id)

        with pytest.raises(KiiObjectBodyNotFoundError):
            deleted = bucket.delete_an_object_body(obj._id)


    def test_publish_an_object_body(self):
        cls = TestApplicationObjectBody
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

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


class TestUtilityMethods:
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        cleanup()
        cls.api = get_api_with_test_user()
        cls.scope = cls.api.buckets.application
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
        except KiiBucketNotFoundError:
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
        except KiiObjectBodyNotFoundError:
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

        added = bucket.retrieve_an_object_body(obj._id)

        assert added.body == body.encode('utf-8')

    def test_verify_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(KiiObjectBodyNotFoundError):
            result = bucket.verify_the_object_body_existence(obj._id)

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

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

        assert obj.has_body() is True

    def test_delete_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(KiiObjectBodyNotFoundError):
            obj.delete_body()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

        obj.delete_body()

    def test_delete_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        with pytest.raises(KiiObjectBodyNotFoundError):
            obj.delete_body()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

        obj.delete_body()

    def test_publish_body(self):
        cls = TestUtilityMethods
        bucket = cls.scope(BUCKET_ID)

        obj = bucket.query().one()

        body = 'abcdefghijklmnopqrstuvwxyz'
        result = bucket.add_or_replace_an_object_body(obj._id, body, 'text/plain')

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


class TestGroupScopeBuckets:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        user = self.api.users.retrieve_user_data()
        self.scope = self.api.buckets.group
        self.group = self.api.groups.create_a_group(GROUP_NAME, user.user_id)

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(self.group.group_id, BUCKET_ID)
        except KiiBucketNotFoundError:
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

        assert isinstance(obj, CreateResult)
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

        bucket = self.scope.retrieve_a_bucket(self.group.group_id, BUCKET_ID)

        assert isinstance(bucket, BucketResult)
        assert bucket.bucket_type == 'READ_WRITE'
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
        self.scope.delete_a_bucket(self.group.group_id, BUCKET_ID)

        with pytest.raises(KiiBucketNotFoundError):
            self.scope.delete_a_bucket(self.group.group_id, BUCKET_ID)


class TestUserScopeBuckets:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        self.scope = self.api.buckets.user

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(BUCKET_ID)
        except KiiBucketNotFoundError:
            pass
        cleanup()

    def test_retrieve_bucket_by_me(self):
        obj = self.scope(BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        bucket = self.scope.retrieve_a_bucket(BUCKET_ID)

        assert isinstance(bucket, BucketResult)
        assert bucket.bucket_type == 'READ_WRITE'
        assert bucket.size > 0

    def test_retrieve_bucket_by_address(self):
        test_user = get_env()['test_user']
        obj = self.scope(BUCKET_ID, account_type='EMAIL', address=test_user['email']).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        bucket = self.scope.retrieve_a_bucket(BUCKET_ID, account_type='EMAIL', address=test_user['email'])

        assert isinstance(bucket, BucketResult)
        assert bucket.bucket_type == 'READ_WRITE'
        assert bucket.size > 0

        bucket2 = self.scope.retrieve_a_bucket(BUCKET_ID, account_type=AccountType.email, address=test_user['email'])

        assert isinstance(bucket2, BucketResult)
        assert bucket2.bucket_type == 'READ_WRITE'
        assert bucket2.size > 0

        bucket3 = self.scope.retrieve_a_bucket(BUCKET_ID, account_type='PHONE', address=test_user['phone'])

        assert isinstance(bucket3, BucketResult)
        assert bucket3.bucket_type == 'READ_WRITE'
        assert bucket3.size > 0

        bucket4 = self.scope.retrieve_a_bucket(BUCKET_ID, account_type=AccountType.phone, address=test_user['phone'])

        assert isinstance(bucket4, BucketResult)
        assert bucket4.bucket_type == 'READ_WRITE'
        assert bucket4.size > 0

    def test_retrieve_bucket_by_id(self):
        test_user = self.api.users.retrieve_user_data()
        obj = self.scope(BUCKET_ID, user_id=test_user.user_id).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        bucket = self.scope.retrieve_a_bucket(BUCKET_ID, user_id=test_user.user_id)

        assert isinstance(bucket, BucketResult)
        assert bucket.bucket_type == 'READ_WRITE'
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
        self.scope.delete_a_bucket(BUCKET_ID)

        with pytest.raises(KiiBucketNotFoundError):
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

        assert isinstance(obj, CreateResult)
        assert obj.object_id
        assert obj.created_at
        assert isinstance(obj.created_at, datetime)
        assert obj.data_type
        assert obj.data_type == 'application/json'

    def test_create_object_by_address(self):
        test_user = get_env()['test_user']
        obj = self.scope(BUCKET_ID, account_type=AccountType.email, address=test_user['email']).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        assert isinstance(obj, CreateResult)
        assert obj.object_id
        assert obj.created_at
        assert isinstance(obj.created_at, datetime)
        assert obj.data_type
        assert obj.data_type == 'application/json'

    def test_create_object_by_id(self):
        test_user = self.api.users.retrieve_user_data()
        obj = self.scope(BUCKET_ID, user_id=test_user.user_id).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

        assert isinstance(obj, CreateResult)
        assert obj.object_id
        assert obj.created_at
        assert isinstance(obj.created_at, datetime)
        assert obj.data_type
        assert obj.data_type == 'application/json'
