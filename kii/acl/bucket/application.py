from kii.acl.base import (
    ACLBaseRequest, ACLVerbMixin, ACLSubjectOnBucket, ACLVerbType,
    SubjectType, SubjectTypeMixin,
)


class BucketArgsMixin:
    def format_args(self):
        args = self._format_args()
        args['bucketID'] = self.bucket_id
        return args


class RetrieveTheCurrentACLEntries(BucketArgsMixin, ACLVerbMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnBucket
    paths = {
        ACLVerbType.all: '/apps/{appID}/buckets/{bucketID}/acl',
        ACLVerbType.acl_verb: '/apps/{appID}/buckets/{bucketID}/acl/{ACLVerb}'
    }

    def __init__(self, api, bucket_id, acl_verb=None):
        super().__init__(api)
        self.bucket_id = bucket_id
        self.acl_verb = acl_verb


class VerifyThePermission(BucketArgsMixin, SubjectTypeMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnBucket
    paths = {
        SubjectType.user: '/apps/{appID}/buckets/{bucketID}/acl/{ACLVerb}/UserID:{subjectUserID}',
        SubjectType.group: '/apps/{appID}/buckets/{bucketID}/acl/{ACLVerb}/GroupID:{subjectGroupID}',  # NOQA
        SubjectType.thing: '/apps/{appID}/buckets/{bucketID}/acl/{ACLVerb}/ThingID:{subjectThingID}',  # NOQA
    }

    def __init__(self, api, bucket_id, acl_verb, *,
                 subject_user_id=None,
                 subject_group_id=None,
                 subject_thing_id=None):
        super().__init__(api)
        self.bucket_id = bucket_id
        self.acl_verb = acl_verb
        self.subject_user_id = subject_user_id
        self.subject_group_id = subject_group_id
        self.subject_thing_id = subject_thing_id


class GrantThePermission(VerifyThePermission):
    method = 'PUT'


class RevokeThePermission(VerifyThePermission):
    method = 'DELETE'
