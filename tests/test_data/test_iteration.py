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
