from kii.acl.base import (
    ACLBaseRequest, ACLVerbMixin, ACLSubjectOnObject, ACLVerbType,
    SubjectType, SubjectTypeMixin,
)


class ObjectArgsMixin:
    def format_args(self):
        args = self._format_args()
        args['bucketID'] = self.bucket_id
        args['objectID'] = self.object_id
        return args


class RetrieveTheCurrentACLEntries(ObjectArgsMixin, ACLVerbMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnObject
    paths = {
        ACLVerbType.all: '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/acl',
        ACLVerbType.acl_verb: '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/acl/{ACLVerb}',
    }

    def __init__(self, api, bucket_id, object_id, acl_verb=None):
        super().__init__(api)
        self.bucket_id = bucket_id
        self.object_id = object_id
        self.acl_verb = acl_verb


class VerifyThePermission(ObjectArgsMixin, SubjectTypeMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnObject
    paths = {
        SubjectType.user: '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/acl/{ACLVerb}/UserID:{subjectUserID}',  # NOQA
        SubjectType.group: '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/acl/{ACLVerb}/GroupID:{subjectGroupID}',  # NOQA
        SubjectType.thing: '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/acl/{ACLVerb}/ThingID:{subjectThingID}',  # NOQA
    }

    def __init__(self, api, bucket_id, object_id, acl_verb, *,
                 subject_user_id=None,
                 subject_group_id=None,
                 subject_thing_id=None):
        super().__init__(api)
        self.bucket_id = bucket_id
        self.object_id = object_id
        self.acl_verb = acl_verb
        self.subject_user_id = subject_user_id
        self.subject_group_id = subject_group_id
        self.subject_thing_id = subject_thing_id


class GrantThePermission(VerifyThePermission):
    method = 'PUT'


class RevokeThePermission(VerifyThePermission):
    method = 'DELETE'
