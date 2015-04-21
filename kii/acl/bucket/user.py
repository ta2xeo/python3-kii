from kii.enums import UserRequestType
from kii.acl.base import (
    ACLBaseRequest, UserACLVerbMixin, ACLSubjectOnBucket, ACLVerbType,
    SubjectType, UserSubjectTypeMixin,
)


class BucketArgsMixin:
    def format_args(self):
        args = self._format_args()
        args['userID'] = self.user_id
        args['bucketID'] = self.bucket_id
        return args


class RetrieveTheCurrentACLEntries(BucketArgsMixin, UserACLVerbMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnBucket
    paths = {
        ACLVerbType.all: {
            UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/buckets/{bucketID}/acl',  # NOQA
            UserRequestType.by_id: '/apps/{appID}/users/{userID}/buckets/{bucketID}/acl',
            UserRequestType.by_me_literal: '/apps/{appID}/users/me/buckets/{bucketID}/acl',
        },
        ACLVerbType.acl_verb: {
            UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/buckets/{bucketID}/acl/{ACLVerb}',  # NOQA
            UserRequestType.by_id: '/apps/{appID}/users/{userID}/buckets/{bucketID}/acl/{ACLVerb}',  # NOQA
            UserRequestType.by_me_literal: '/apps/{appID}/users/me/buckets/{bucketID}/acl/{ACLVerb}',  # NOQA
        }
    }

    def __init__(self, api, bucket_id, acl_verb=None, *,
                 account_type=None, address=None, user_id=None):
        super().__init__(api)
        self.bucket_id = bucket_id
        self.acl_verb = acl_verb
        self.account_type = account_type
        self.address = address
        self.user_id = user_id


class VerifyThePermission(BucketArgsMixin, UserSubjectTypeMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnBucket
    paths = {
        SubjectType.user: {
            UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/buckets/{bucketID}/acl/{ACLVerb}/UserID:{subjectUserID}',  # NOQA
            UserRequestType.by_id: '/apps/{appID}/users/{userID}/buckets/{bucketID}/acl/{ACLVerb}/UserID:{subjectUserID}',  # NOQA
            UserRequestType.by_me_literal: '/apps/{appID}/users/me/buckets/{bucketID}/acl/{ACLVerb}/UserID:{subjectUserID}',  # NOQA
        },
        SubjectType.group: {
            UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/buckets/{bucketID}/acl/{ACLVerb}/GroupID:{subjectGroupID}',  # NOQA
            UserRequestType.by_id: '/apps/{appID}/users/{userID}/buckets/{bucketID}/acl/{ACLVerb}/GroupID:{subjectGroupID}',  # NOQA
            UserRequestType.by_me_literal: '/apps/{appID}/users/me/buckets/{bucketID}/acl/{ACLVerb}/GroupID:{subjectGroupID}',  # NOQA
        },
        SubjectType.thing: {
            UserRequestType.by_address: '/apps/{appID}/users/{accountType}:{address}/buckets/{bucketID}/acl/{ACLVerb}/ThingID:{subjectThingID}',  # NOQA
            UserRequestType.by_id: '/apps/{appID}/users/{userID}/buckets/{bucketID}/acl/{ACLVerb}/ThingID:{subjectThingID}',  # NOQA
            UserRequestType.by_me_literal: '/apps/{appID}/users/me/buckets/{bucketID}/acl/{ACLVerb}/ThingID:{subjectThingID}',  # NOQA
        },
    }

    def __init__(self, api, bucket_id, acl_verb, *,
                 account_type=None,
                 address=None,
                 user_id=None,
                 subject_user_id=None,
                 subject_group_id=None,
                 subject_thing_id=None):
        super().__init__(api)
        self.acl_verb = acl_verb
        self.bucket_id = bucket_id
        self.account_type = account_type
        self.address = address
        self.user_id = user_id
        self.subject_user_id = subject_user_id
        self.subject_group_id = subject_group_id
        self.subject_thing_id = subject_thing_id


class GrantThePermission(VerifyThePermission):
    method = 'PUT'


class RevokeThePermission(VerifyThePermission):
    method = 'DELETE'
