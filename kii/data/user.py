# User Scope Bucket
from kii.data.application import (
    RetrieveABucket as BaseRetrieveABucket,
    DeleteABucket as BaseDeleteABucket,
    CreateAnObject as BaseCreateAnObject,
)
from kii.enums import UserRequestType
from kii.users import AccountTypeMixin


class AbstractManageMixin:
    @property
    def by_address(self):
        return UserRequestType.by_address

    @property
    def by_id(self):
        return UserRequestType.by_id

    @property
    def by_me_literal(self):
        return UserRequestType.by_me_literal

    def format_args(self):
        def by_address():
            return {
                'appID': self.api.app_id,
                'accountType': self.account_type,
                'address': self.address,
                'bucketID': self.bucket_id,
            }

        def by_id():
            return {
                'appID': self.api.app_id,
                'userID': self.user_id,
                'bucketID': self.bucket_id,
            }

        def by_me_literal():
            return {
                'appID': self.api.app_id,
                'bucketID': self.bucket_id,
            }

        return {
            self.by_address: by_address,
            self.by_id: by_id,
            self.by_me_literal: by_me_literal,
        }[self.request_type]()


# Manage Buckets
class ManageBucketsMixin(AbstractManageMixin, AccountTypeMixin):
    paths = {
        UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/buckets/{bucketID}',  # NOQA
        UserRequestType.by_id: '/apps/{appID}/users/{userID}/buckets/{bucketID}',
        UserRequestType.by_me_literal: '/apps/{appID}/users/me/buckets/{bucketID}',
    }

    @property
    def api_path(self):
        UserScope = self.scope.__class__

        self.request_type = UserScope.get_request_type(self.api,
                                                       self.account_type,
                                                       self.address,
                                                       self.user_id)
        return self.paths[self.request_type].format(**self.format_args())


class RetrieveABucket(ManageBucketsMixin, BaseRetrieveABucket):
    def __init__(self, scope, bucket_id, *,
                 account_type=None, address=None, user_id=None):
        super().__init__(scope, bucket_id)
        self.account_type = account_type
        self.address = address
        self.user_id = user_id


class DeleteABucket(ManageBucketsMixin, BaseDeleteABucket):
    def __init__(self, scope, bucket_id, *,
                 account_type=None, address=None, user_id=None):
        super().__init__(scope, bucket_id)
        self.account_type = account_type
        self.address = address
        self.user_id = user_id


# Manage Objects
class ManageObjectsMixin(AbstractManageMixin):
    @property
    def account_type(self):
        return self.scope.account_type

    @property
    def address(self):
        return self.scope.address

    @property
    def user_id(self):
        return self.scope.user_id

    @property
    def request_type(self):
        return self.scope.request_type

    @property
    def api_path(self):
        return self.paths[self.request_type].format(**self.format_args())


class CreateAnObject(ManageObjectsMixin, BaseCreateAnObject):
    paths = {
        UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/buckets/{bucketID}/objects',  # NOQA
        UserRequestType.by_id: '/apps/{appID}/users/{userID}/buckets/{bucketID}/objects',
        UserRequestType.by_me_literal: '/apps/{appID}/users/me/buckets/{bucketID}/objects',
    }
