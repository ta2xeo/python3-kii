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

    def test_query_count(self):
        cls = TestApplicationQuery
        bucket = cls.scope(BUCKET_ID)

        # all
        query = bucket.query()
        results = query.all()
        count = query.count()
        assert len(results) == self.OBJ_COUNT
        assert count == self.OBJ_COUNT

        # query
        clause = cl.EqualClause('even', True)
        query = bucket.query(clause)
        results = query.all()
        count = query.count()
        assert len(results) == int(self.OBJ_COUNT / 2)
        assert count == int(self.OBJ_COUNT / 2)
