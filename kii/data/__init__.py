from enum import Enum, unique
import os

from kii import exceptions as exc
from kii.data import (
    application as ApplicationScopeBucket,
    group as GroupScopeBucket,
    user as UserScopeBucket,
    clauses,
)
from kii.enums import UserRequestType
from kii.users import AccountTypeMixin
from kii.utils import Accessor


RESERVED_WORDS = ('users', 'devices', 'internal', 'things')


@unique
class BucketType(Enum):
    READ_WRITE = 'rw'


class DataManagement:
    def __init__(self, api):
        self.application = ApplicationScope(api, Accessor(ApplicationScopeBucket))
        self.group = GroupScope(api, Accessor(GroupScopeBucket))
        self.user = UserScope(api, Accessor(UserScopeBucket))


class Scope:
    def request(self, cls, *args, **kwargs):
        helper = cls(self, *args, **kwargs)
        if not helper.bucket_id:
            raise exc.KiiInvalidBucketIdError

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

    def query(self, *clause):
        """
        SQLAlchemy like method
        """
        argc = len(clause)
        if argc >= 2:
            clause = clauses.AndClause(*clause)
        elif argc == 1:
            clause = clause[0]
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
        except exc.KiiObjectBodyNotFoundError:
            return False

    def delete_an_object_body(self, object_id):
        return self.request(self.scope.DeleteAnObjectBody, object_id)

    def publish_an_object_body(self, object_id, *,
                               expires_at=None, expires_in=None):
        return self.request(self.scope.PublishAnObjectBody, object_id,
                            expires_at=expires_at, expires_in=expires_in)

    def start_uploading_an_object_body(self, object_id):
        return self.request(self.scope.StartUploadingAnObjectBody, object_id)

    def get_the_upload_metadata(self, object_id, upload_id):
        return self.request(self.scope.GetTheUploadMetadata, object_id, upload_id)

    def upload_the_given_object_data(self, object_id, upload_id, body, content_type,
                                     start_byte, end_byte, total_byte):
        return self.request(self.scope.UploadTheGivenObjectData,
                            object_id, upload_id, body, content_type,
                            start_byte, end_byte, total_byte)

    def set_the_object_body_upload_status_to_committed(self, object_id, upload_id):
        return self.request(self.scope.SetTheObjectBodyUploadStatusToCommitted,
                            object_id, upload_id)

    def set_the_object_body_upload_status_to_cancelled(self, object_id, upload_id):
        return self.request(self.scope.SetTheObjectBodyUploadStatusToCancelled,
                            object_id, upload_id)

    def upload_body_multiple_pieces(self, object_id, fileobj, content_type,
                                    piece_byte=1024 * 1024):  # 1MB
        upload_id = self.start_uploading_an_object_body(object_id).upload_id
        filesize = os.fstat(fileobj.fileno()).st_size

        def upload():
            size, start, end = 0, 0, piece_byte

            while True:
                # tail
                if end >= filesize:
                    end = filesize - 1

                size = end - start + 1
                self.upload_the_given_object_data(object_id, upload_id, fileobj.read(size),
                                                  content_type, start, end, filesize)

                if end + 1 >= filesize:
                    break

                start = end + 1
                end = start + piece_byte

            self.set_the_object_body_upload_status_to_committed(object_id, upload_id)

        try:
            upload()
            return True
        except:
            self.set_the_object_body_upload_status_to_cancelled(object_id, upload_id)
            return False


class ApplicationScope(Scope):
    def __init__(self, api, scope, bucket_id=None):
        self.api = api
        self.scope = scope
        self.bucket_id = bucket_id

    def __call__(self, bucket_id):
        if bucket_id in RESERVED_WORDS or bucket_id.startswith('_'):
            raise exc.KiiInvalidBucketIdError

        if not bucket_id:
            raise exc.KiiInvalidBucketIdError

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
            raise exc.KiiInvalidBucketIdError

        if not group_id:
            raise exc.KiiInvalidGroupIdError

        if not bucket_id:
            raise exc.KiiInvalidBucketIdError

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
            raise exc.KiiInvalidBucketIdError

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
            return UserRequestType.by_address

        elif user_id:
            return UserRequestType.by_id

        else:
            # http://documentation.kii.com/en/guides/rest/admin-features/
            if isinstance(api, KiiAdminAPI):
                raise exc.KiiIllegalAccessError

        return UserRequestType.by_me_literal

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
