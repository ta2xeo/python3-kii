from datetime import datetime
from enum import Enum

from kii.buckets import (
    application as ApplicationScopeBucket,
    group as GroupScopeBucket,
    user as UserScopeBucket,
)
from kii.buckets.clauses import (
    Clause,
    AndClause,
)
from kii.exceptions import *
from kii.helpers import BucketsHelper
from kii.results import *
from kii.users import (
    AccountType,
    AccountTypeMixin,
)


RESERVED_WORDS = ('users', 'devices', 'internal', 'things')


class Accessor:
    def __init__(self, scope):
        self.scope = scope

    def __getattr__(self, name):
        try:
            return getattr(self.scope, name)
        except AttributeError as e:
            raise KiiNotImplementedError('{0} is not implemented in {1} scope.'.format(name, self.scope)) from e


class Buckets:
    def __init__(self, api):
        self.application = ApplicationScope(api, Accessor(ApplicationScopeBucket))
        self.group = GroupScope(api, Accessor(GroupScopeBucket))
        self.user = UserScope(api, Accessor(UserScopeBucket))


class Scope:
    def request(self, cls, *args, **kwargs):
        helper = cls(self, *args, **kwargs)
        return helper.request()

    def create_an_object(self, params):
        return self.request(self.scope.CreateAnObject, params)

    def retrieve_an_object(self, object_id):
        return self.request(self.scope.RetrieveAnObject, object_id)

    def fully_update_an_object(self, object_id, data,
                               *, if_match=None, if_none_match=None):
        return self.request(self.scope.FullyUpdateAnObject, object_id, data,
                            if_match=if_match,
                            if_none_match=if_none_match)

    def create_a_new_object_with_an_id(self, object_id, data,
                                       *, if_match=None, if_none_match=None):
        return self.request(self.scope.CreateANewObjectWithAnID, object_id, data,
                            if_match=if_match,
                            if_none_match=if_none_match)

    def partially_update_an_object(self, object_id, data,
                                   *, if_match=None, if_none_match=None):
        return self.request(self.scope.PartiallyUpdateAnObject, object_id, data,
                            if_match=if_match,
                            if_none_match=if_none_match)

    def delete_an_object(self, object_id, *, if_match=None, if_none_match=None):
        return self.request(self.scope.DeleteAnObject, object_id,
                            if_match=if_match,
                            if_none_match=if_none_match)

    def query_for_objects(self, clause=None, **kwargs):
        return self.request(self.scope.QueryForObjects, clause, **kwargs)

    def query(self, *clauses):
        """
        SQLAlchemy like method
        """
        argc = len(clauses)
        if argc >= 2:
            clause = AndClause(*clauses)
        elif argc == 1:
            clause = clauses[0]
        else:
            clause = None

        return self.scope.QueryForObjects(self, clause)

    def retrieve_an_object_body(self, object_id, *,
                                if_match=None, range=None):
        return self.request(self.scope.RetrieveAnObjectBody, object_id,
                            if_match=if_match, range=range)

    def add_or_replace_an_object_body(self, object_id, body, content_type, *,
                                      if_match=None, if_none_match=None):
        return self.request(self.scope.AddOrReplaceAnObjectBody,
                            object_id, body, content_type,
                            if_match=if_match, if_none_match=if_none_match)

    def verify_the_object_body_existence(self, object_id):
        return self.request(self.scope.VerifyTheObjectBodyExistence, object_id)

    def has_body(self, object_id):
        try:
            self.verify_the_object_body_existence(object_id)
            return True
        except KiiObjectBodyNotFoundError:
            return False

    def delete_an_object_body(self, object_id):
        return self.request(self.scope.DeleteAnObjectBody, object_id)

    def publish_an_object_body(self, object_id, *,
                               expires_at=None, expires_in=None):
        return self.request(self.scope.PublishAnObjectBody, object_id,
                            expires_at=expires_at, expires_in=expires_in)


class ApplicationScope(Scope):
    def __init__(self, api, scope, bucket_id=None):
        self.api = api
        self.scope = scope
        self.bucket_id = bucket_id

    def __call__(self, bucket_id):
        if bucket_id in RESERVED_WORDS or bucket_id.startswith('_'):
            raise KiiInvalidBucketIdError

        if not bucket_id:
            raise KiiInvalidBucketIdError

        return ApplicationScope(self.api, self.scope, bucket_id)

    def retrieve_a_bucket(self, bucket_id):
        req = self.scope.RetrieveABucket(self, bucket_id)
        result = req.request()
        return result

    def delete_a_bucket(self, bucket_id):
        req = self.scope.DeleteABucket(self, bucket_id)
        result = req.request()
        return result


class GroupScope(ApplicationScope):
    def __init__(self, api, scope, group_id=None, bucket_id=None):
        self.api = api
        self.scope = scope
        self.group_id = group_id
        self.bucket_id = bucket_id

    def __call__(self, group_id, bucket_id):
        if bucket_id in RESERVED_WORDS or bucket_id.startswith('_'):
            raise KiiInvalidBucketIdError

        if not group_id:
            raise KiiInvalidGroupIdError

        if not bucket_id:
            raise KiiInvalidBucketIdError

        return GroupScope(self.api, self.scope, group_id, bucket_id)

    def retrieve_a_bucket(self, group_id, bucket_id):
        req = self.scope.RetrieveABucket(self, group_id, bucket_id)
        result = req.request()
        return result

    def delete_a_bucket(self, group_id, bucket_id):
        req = self.scope.DeleteABucket(self, group_id, bucket_id)
        result = req.request()
        return result


class UserScope(AccountTypeMixin, ApplicationScope):
    class RequestType(Enum):
        by_address = 1
        by_id = 2
        by_me_literal = 3

    def __init__(self, api, scope, bucket_id=None, *,
                 account_type=None, address=None, user_id=None):
        self.api = api
        self.scope = scope
        self.bucket_id = bucket_id
        self.account_type = account_type
        self.address = address
        self.user_id = user_id

    def __call__(self, bucket_id, *,
                 account_type=None, address=None, user_id=None):
        if bucket_id in RESERVED_WORDS or bucket_id.startswith('_'):
            raise KiiInvalidBucketIdError

        return UserScope(self.api, self.scope, bucket_id,
                         account_type=account_type, address=address, user_id=user_id)

    @property
    def request_type(self):
        return UserScope.get_request_type(self.api,
                                          self.account_type,
                                          self.address,
                                          self.user_id)

    @classmethod
    def get_request_type(cls, api, account_type, address, user_id):
        from kii.api import KiiAdminAPI

        if account_type and address:
            return cls.RequestType.by_address

        elif user_id:
            return cls.RequestType.by_id

        else:
            # http://documentation.kii.com/en/guides/rest/admin-features/
            if isinstance(api, KiiAdminAPI):
                raise KiiIllegalAccessError

        return cls.RequestType.by_me_literal

    def retrieve_a_bucket(self, bucket_id, *, account_type=None, address=None, user_id=None):
        req = self.scope.RetrieveABucket(self,
                                         bucket_id,
                                         account_type=account_type,
                                         address=address,
                                         user_id=user_id)
        result = req.request()
        return result

    def delete_a_bucket(self, bucket_id, *, account_type=None, address=None, user_id=None):
        req = self.scope.DeleteABucket(self,
                                       bucket_id,
                                       account_type=account_type,
                                       address=address,
                                       user_id=user_id)
        result = req.request()
        return result
