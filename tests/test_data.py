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

from .conf import (
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


class TestApplicationQuery:
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        cleanup()
        cls.api = get_api_with_test_user()
        cls.scope = cls.api.data.application
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

    def test_query_all(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        # all
        results = bucket.query().all()
        assert len(results) == cls.OBJ_COUNT

        results = bucket.query(cl.RangeClause('index').lt(4)).all()
        assert len(results) == 4

        results = bucket.query(
            cl.RangeClause('index').lt(8),
            cl.EqualClause('even', False),
        ).all()
        assert len(results) == 4

        results = bucket.query(cl.EqualClause('index', -1)).all()
        assert len(results) == 0

    def test_query_one(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        # one
        result = bucket.query(cl.EqualClause('index', 1)).one()
        assert isinstance(result, rs.ObjectResult)
        assert result._created
        assert result._modified
        assert result._owner
        assert result._version == 1

        with pytest.raises(exc.KiiMultipleResultsFoundError):
            bucket.query(cl.EqualClause('name', 'test user')).one()

        with pytest.raises(exc.KiiObjectNotFoundError):
            bucket.query(cl.EqualClause('name', 'unknown')).one()

    def test_query_first(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        # first
        result = bucket.query(cl.EqualClause('index', 1)).first()
        assert isinstance(result, rs.ObjectResult)
        assert result._created
        assert result._modified
        assert result._owner
        assert result._version == 1

        result = bucket.query(cl.EqualClause('index', -1)).first()
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

    def test_query_offset(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        query = bucket.query().limit(3)
        results = query.all()
        assert len(results) == 3
        for i, r in enumerate(results):
            assert r['index'] == i

        query = query.offset(3)
        results = query.all()
        assert len(results) == 3
        for i, r in enumerate(results):
            assert r['index'] == i + 3

        query = query.offset(6)
        results = query.all()
        assert len(results) == 3
        for i, r in enumerate(results):
            assert r['index'] == i + 6

        query = query.offset(cls.OBJ_COUNT - 2)
        results = query.all()
        assert len(results) == 2
        for i, r in enumerate(results):
            assert r['index'] == i + cls.OBJ_COUNT - 2


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


class TestIteration:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        self.scope = self.api.data.application
        self.bucket = self.scope(BUCKET_ID)
        self.OBJ_COUNT = 10
        self._create_test_objects()

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(BUCKET_ID)
        except exc.KiiBucketNotFoundError:
            pass
        cleanup()

    def _create_test_objects(self):
        for i in range(self.OBJ_COUNT):
            even = i % 2 == 0
            self.bucket.create_an_object({
                'index': i,
                'desc': 'An object number is {0}.'.format(i + 1),
                'name': 'test user',
                'even': even,
            })

    def test_query_all_objects(self):
        # all
        results = self.bucket.query().best_effort_limit(50).all()
        assert len(results) == self.OBJ_COUNT

    def test_best_effort_limit_greater_than_limit(self):
        # best effort limit
        LIMIT = 1
        BEST_EFFORT_LIMIT = 5
        results = self.bucket.query() \
                             .best_effort_limit(BEST_EFFORT_LIMIT) \
                             .limit(LIMIT).order_by('index', False).all()
        assert len(results) == LIMIT
        assert results[0]['index'] == 0

    def test_best_effort_limit_less_than_limit(self):
        LIMIT = 5
        BEST_EFFORT_LIMIT = 1
        results = self.bucket.query() \
                             .best_effort_limit(BEST_EFFORT_LIMIT) \
                             .limit(LIMIT).order_by('index', False).all()
        assert len(results) == LIMIT

    def test_best_effort_limit(self):
        BEST_EFFORT_LIMIT = 2
        results = self.bucket.query() \
                             .best_effort_limit(BEST_EFFORT_LIMIT) \
                             .order_by('index', False).all()
        assert len(results) == self.OBJ_COUNT

    def test_limit(self):
        LIMIT = 2
        results = self.bucket.query() \
                             .limit(LIMIT) \
                             .order_by('index', False).all()
        assert len(results) == LIMIT

    def test_slice(self):
        results = self.bucket.query().all()
        assert len(results[:5]) == 5
        for i, r in enumerate(results[:5]):
            assert r['index'] == i

        assert len(results[3:]) == self.OBJ_COUNT - 3
        for i, r in enumerate(results[3:]):
            assert r['index'] == 3 + i

    def test_offset(self):
        OFFSET = 2
        results = self.bucket.query() \
                             .offset(OFFSET) \
                             .order_by('index', False).all()
        assert len(results) == self.OBJ_COUNT - OFFSET
        assert results[0]['index'] == OFFSET

    def test_offset_and_limit(self):
        OFFSET = 3
        LIMIT = 3
        results = self.bucket.query() \
                             .offset(OFFSET) \
                             .limit(LIMIT) \
                             .order_by('index', False).all()
        assert len(results) == LIMIT
        for i, r in enumerate(results):
            assert r['index'] == i + OFFSET

    def test_offset_and_limit_and_best_effort_limit(self):
        OFFSET = 1
        LIMIT = 6
        BEST_EFFORT_LIMIT = 2
        results = self.bucket.query() \
                             .offset(OFFSET) \
                             .limit(LIMIT) \
                             .best_effort_limit(BEST_EFFORT_LIMIT) \
                             .order_by('index', False).all()
        assert len(results) == LIMIT
        for i, r in enumerate(results):
            assert r['index'] == i + OFFSET

    def test_pop(self):
        results = self.bucket.query() \
                             .order_by('index', False).all()

        assert len(results) == self.OBJ_COUNT

        last = results.pop()
        assert last
        assert last['index'] == self.OBJ_COUNT - 1
        assert len(results) == self.OBJ_COUNT - 1

        for i, r in enumerate(results):
            assert r['index'] == i

        head = results.pop(0)
        assert head['index'] == 0
        assert len(results) == self.OBJ_COUNT - 2

        for i, r in enumerate(results):
            assert r['index'] == i + 1

    def test_pop_and_limit(self):
        LIMIT = 7
        results = self.bucket.query() \
                             .limit(LIMIT) \
                             .order_by('index', False).all()

        assert len(results) == LIMIT

        last = results.pop()
        assert last
        assert last['index'] == LIMIT - 1
        assert len(results) == LIMIT - 1

        for i, r in enumerate(results):
            assert r['index'] == i

        head = results.pop(0)
        assert head['index'] == 0
        assert len(results) == LIMIT - 2

        for i, r in enumerate(results):
            assert r['index'] == i + 1

    def test_pop_and_best_effort_limit(self):
        BEST_EFFORT_LIMIT = 2
        results = self.bucket.query() \
                             .best_effort_limit(BEST_EFFORT_LIMIT) \
                             .order_by('index', False).all()

        assert len(results) == self.OBJ_COUNT

        last = results.pop()
        assert last
        assert last['index'] == self.OBJ_COUNT - 1
        assert len(results) == self.OBJ_COUNT - 1

        for i, r in enumerate(results):
            assert r['index'] == i

        head = results.pop(0)
        assert head['index'] == 0
        assert len(results) == self.OBJ_COUNT - 2

        for i, r in enumerate(results):
            assert r['index'] == i + 1

    def test_pop_and_offset(self):
        OFFSET = 2
        results = self.bucket.query() \
                             .offset(OFFSET) \
                             .order_by('index', False).all()

        assert len(results) == self.OBJ_COUNT - OFFSET

        last = results.pop()
        assert last
        assert last['index'] == self.OBJ_COUNT - 1
        assert len(results) == self.OBJ_COUNT - OFFSET - 1

        for i, r in enumerate(results):
            assert r['index'] == i + OFFSET

        head = results.pop(0)
        assert head['index'] == OFFSET
        assert len(results) == self.OBJ_COUNT - OFFSET - 2

        for i, r in enumerate(results):
            assert r['index'] == i + 1 + OFFSET

    def test_pop_and_limit_and_best_effort_limit_and_offset(self):
        OFFSET = 2
        BEST_EFFORT_LIMIT = 2
        LIMIT = 4
        results = self.bucket.query() \
                             .limit(LIMIT) \
                             .best_effort_limit(BEST_EFFORT_LIMIT) \
                             .offset(OFFSET) \
                             .order_by('index', False).all()

        assert len(results) == LIMIT

        last = results.pop()
        assert last
        assert last['index'] == OFFSET + LIMIT - 1
        assert len(results) == LIMIT - 1

        for i, r in enumerate(results):
            assert r['index'] == i + OFFSET

        head = results.pop(0)
        assert head['index'] == OFFSET
        assert len(results) == LIMIT - 2

        for i, r in enumerate(results):
            assert r['index'] == i + 1 + OFFSET

    def test_pop_zero(self):
        results = self.bucket.query() \
                             .order_by('index', False).all()

        assert len(results) == self.OBJ_COUNT
        counter = 0
        while results:
            counter += 1
            last = results.pop()
            if not last:
                break
            assert last
            assert last['index'] == self.OBJ_COUNT - counter
            if last['index'] == 0:
                assert bool(results) is False
            else:
                assert bool(results) is True

        assert counter == self.OBJ_COUNT
