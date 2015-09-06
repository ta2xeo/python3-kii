# Application Scope Bucket
from datetime import datetime
import json

from kii import exceptions as exc, results as rs
from kii.data.clauses import (
    Clause,
    AllClause,
    AndClause,
)
from kii.helpers import BucketsHelper


# Manage Buckets
class ManageBuckets(BucketsHelper):
    def __init__(self, scope, bucket_id):
        super().__init__(scope)
        self.bucket_id = bucket_id

    @property
    def bucket_id(self):
        return self._bucket_id

    @bucket_id.setter
    def bucket_id(self, bucket_id):
        self._bucket_id = bucket_id

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id)

    @property
    def headers(self):
        headers = super().headers
        if self.access_token:
            headers['Authorization'] = self.authorization

        return headers


class RetrieveABucket(ManageBuckets):
    method = 'GET'
    result_container = rs.BucketResult


class DeleteABucket(ManageBuckets):
    method = 'DELETE'
    result_container = rs.BaseResult


# Manage Objects
class CreateAnObject(BucketsHelper):
    method = 'POST'
    result_container = rs.CreateResult

    def __init__(self, scope, data):
        super().__init__(scope)
        self.data = data

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Content-Type'] = 'application/json'

        if self.access_token:
            headers['Authorization'] = self.authorization

        return headers

    def request(self):
        return super().request(json=self.data)


class RetrieveAnObject(BucketsHelper):
    method = 'GET'
    result_container = rs.ObjectResult

    def __init__(self, scope, object_id):
        super().__init__(scope)
        self.object_id = object_id

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Content-Type'] = 'application/json'
        return headers


class FullyUpdateAnObject(BucketsHelper):
    method = 'PUT'
    result_container = rs.UpdateResult

    def __init__(self, scope, object_id, data, *, if_match=None, if_none_match=None):
        super().__init__(scope)
        self.object_id = object_id
        self.data = data
        self.if_match = if_match
        self.if_none_match = if_none_match

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Content-Type'] = 'application/json'

        if self.access_token:
            headers['Authorization'] = self.authorization

        if self.if_match:
            headers['If-Match'] = self.if_match

        if self.if_none_match:
            headers['If-None-Match'] = self.if_none_match

        return headers

    def request(self):
        return super().request(json=self.data)


class CreateANewObjectWithAnID(FullyUpdateAnObject):
    """
    synonym of FullyUpdateAnObject
    """


class PartiallyUpdateAnObject(FullyUpdateAnObject):
    method = 'POST'

    @property
    def headers(self):
        headers = super().headers
        headers['X-HTTP-Method-Override'] = 'PATCH'
        headers['Content-Type'] = 'application/json'

        if self.access_token:
            headers['Authorization'] = self.authorization

        if self.if_match:
            headers['If-Match'] = self.if_match

        if self.if_none_match:
            headers['If-None-Match'] = self.if_none_match

        return headers


class DeleteAnObject(BucketsHelper):
    method = 'DELETE'
    result_container = rs.DeleteResult

    def __init__(self, scope, object_id, *, if_match=None, if_none_match=None):
        super().__init__(scope)
        self.object_id = object_id
        self.if_match = if_match
        self.if_none_match = if_none_match

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Content-Type'] = 'application/json'

        if self.access_token:
            headers['Authorization'] = self.authorization

        if self.if_match:
            headers['If-Match'] = self.if_match

        if self.if_none_match:
            headers['If-None-Match'] = self.if_none_match

        return headers


class QueryForObjects(BucketsHelper):
    method = 'POST'
    result_container = rs.QueryResult

    def __init__(self, scope,
                 clause=None,
                 *,
                 order_by=None,
                 descending=None,
                 pagination_key=None,
                 best_effort_limit=None,
                 limit=None):

        super().__init__(scope)
        self.internal = False

        if clause is None:
            clause = AllClause()

        self.clause = clause
        self._order_by = order_by
        self._descending = descending
        self._pagination_key = pagination_key
        self._best_effort_limit = best_effort_limit
        self._limit = limit
        self._offset = 0
        self._aggregations = []

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/query'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Content-Type'] = 'application/vnd.kii.QueryRequest+json'
        return headers

    @property
    def clause(self):
        return self._clause

    @clause.setter
    def clause(self, clause):
        if not isinstance(clause, Clause):
            raise exc.KiiInvalidClauseError

        self._clause = clause

    def clone(self):
        instance = self.__class__(self.scope, self.clause)
        instance._order_by = self._order_by
        instance._descending = self._descending
        instance._pagination_key = self._pagination_key
        instance._best_effort_limit = self._best_effort_limit
        instance._limit = self._limit
        instance._offset = self._offset
        return instance

    def filter(self, *clauses):
        instance = self.clone()
        instance.clause = AndClause(instance.clause, *clauses)
        return instance

    def request(self):
        return super().request(json=self._assemble())

    def bucket_query(self):
        query = {}

        query['clause'] = self.clause.query()

        if self._order_by is not None:
            query['orderBy'] = self._order_by

            if self._descending is not None:
                query['descending'] = self._descending

        if self._aggregations:
            query['aggregations'] = self._aggregations

        return query

    def _assemble(self):
        params = {}
        query = self.bucket_query()
        if query:
            params['bucketQuery'] = query

        if self._pagination_key:
            params['paginationKey'] = self._pagination_key

        if self._limit and self._best_effort_limit is None:
            self._best_effort_limit = self._limit

        if self._best_effort_limit:
            params['bestEffortLimit'] = self._best_effort_limit + self._offset

        return params

    def all(self):
        return self.request()

    def count(self):
        self.result_container = rs.QueryCountResult
        self._aggregations = [
            {
                "type": "COUNT",
                "putAggregationInto": "count_field"
            }
        ]
        result = self.request()
        return result.count

    def first(self):
        results = self.request()
        try:
            return results[0]
        except IndexError:
            return None

    def one(self):
        results = self.request()
        if len(results) > 1:
            raise exc.KiiMultipleResultsFoundError
        try:
            return results[0]
        except IndexError as e:
            raise exc.KiiObjectNotFoundError from e

    def offset(self, offset):
        self._offset = offset
        return self

    def step(self, step):
        self._step = step
        return self

    def best_effort_limit(self, best_effort_limit):
        self._best_effort_limit = best_effort_limit
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def order_by(self, key, descending=True):
        self._order_by = key
        self._descending = descending
        return self

    def pagination_key(self, pagination_key):
        self._pagination_key = pagination_key
        return self

    def __str__(self):
        headers = json.dumps(self.headers, ensure_ascii=False, indent=4, sort_keys=True)
        query = json.dumps(self._assemble(), ensure_ascii=False, indent=4, sort_keys=True)
        return '''\
[{method}] {url}

Headers:
{headers}

Query Request:
{query}'''.format(method=self.method,
                  url=self.url,
                  headers=headers,
                  query=query)


class RetrieveAnObjectBody(BucketsHelper):
    method = 'GET'
    result_container = rs.BodyResult

    def __init__(self, scope, object_id, *,
                 if_match=None,
                 range=None):
        super().__init__(scope)
        self.object_id = object_id
        self.if_match = if_match

        # range is tuple or list. e.g.) [begin, end]
        if range is not None and not isinstance(range, (list, tuple)):
            raise exc.KiiInvalidTypeError

        self.range = range

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Accept'] = '*/*'

        if self.access_token:
            headers['Authorization'] = self.authorization

        if self.if_match:
            headers['If-Match'] = self.if_match

        if self.range:
            headers['Range'] = 'bytes={0}-{1}'.format(*self.range)

        return headers


class AddOrReplaceAnObjectBody(BucketsHelper):
    method = 'PUT'
    result_container = rs.BaseResult

    def __init__(self, scope, object_id, body, content_type, *,
                 if_match=None, if_none_match=None):
        super().__init__(scope)
        self.object_id = object_id
        self.body = body
        self.content_type = content_type
        self.if_match = if_match
        self.if_none_match = if_none_match

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Content-Type'] = self.content_type

        if self.access_token:
            headers['Authorization'] = self.authorization

        if self.if_match:
            headers['If-Match'] = self.if_match

        if self.if_none_match:
            headers['If-None-Match'] = self.if_none_match

        return headers

    def request(self):
        return super().request(data=self.body)


class VerifyTheObjectBodyExistence(BucketsHelper):
    method = 'HEAD'
    result_container = rs.ObjectResult

    def __init__(self, scope, object_id):
        super().__init__(scope)
        self.object_id = object_id

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers

        if self.access_token:
            headers['Authorization'] = self.authorization

        return headers


class DeleteAnObjectBody(BucketsHelper):
    method = 'DELETE'
    result_container = rs.ObjectResult

    def __init__(self, scope, object_id):
        super().__init__(scope)
        self.object_id = object_id

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers

        if self.access_token:
            headers['Authorization'] = self.authorization

        return headers


class PublishAnObjectBody(BucketsHelper):
    method = 'POST'
    result_container = rs.PublishBodyResult

    def __init__(self, scope, object_id, *,
                 expires_at=None, expires_in=None):
        """
        expires_at: The date in Unix epoch in milliseconds
                    when the publication URL should expire
        expires_in: The period in seconds the publication URL
                    has to be available, after that it will expire
        """

        super().__init__(scope)
        self.object_id = object_id
        self.expires_at = expires_at
        self.expires_in = expires_in

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body/publish'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Content-Type'] = 'application/vnd.kii.ObjectBodyPublicationRequest+json'

        if self.access_token:
            headers['Authorization'] = self.authorization

        return headers

    def request(self):
        data = {}

        if self.expires_at is not None:
            if not isinstance(self.expires_at, datetime):
                raise exc.KiiInvalidExpirationError

            expire = int(self.expires_at.timestamp() * 1000)

            data['expiresAt'] = expire

        if self.expires_in is not None:
            data['expiresIn'] = self.expires_in

        return super().request(json=data)
