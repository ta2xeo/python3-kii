# Group Scope Bucket
from kii.buckets.application import (
    RetrieveABucket as BaseRetrieveABucket,
    DeleteABucket as BaseDeleteABucket,
    CreateAnObject as BaseCreateAnObject,
)


# Manage Buckets
class ManageBucketsMixin:
    @property
    def api_path(self):
        return '/apps/{appID}/groups/{groupID}/buckets/{bucketID}'.format(
            appID=self.api.app_id,
            groupID=self.group_id,
            bucketID=self.bucket_id)


class RetrieveABucket(ManageBucketsMixin, BaseRetrieveABucket):
    def __init__(self, scope, group_id, bucket_id):
        super().__init__(scope, bucket_id)
        self.group_id = group_id


class DeleteABucket(ManageBucketsMixin, BaseDeleteABucket):
    def __init__(self, scope, group_id, bucket_id):
        super().__init__(scope, bucket_id)
        self.group_id = group_id


# Manage Objects
class ManageObjectsMixin:
    @property
    def group_id(self):
        return self.scope.group_id


class CreateAnObject(ManageObjectsMixin, BaseCreateAnObject):
    @property
    def api_path(self):
        return '/apps/{appID}/groups/{groupID}/buckets/{bucketID}/objects'.format(
            appID=self.api.app_id,
            groupID=self.group_id,
            bucketID=self.bucket_id,
        )
