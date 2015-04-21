from kii.acl.base import (
    ACLBaseRequest, ACLVerbMixin, ACLVerbType,
    SubjectType, SubjectTypeMixin,
)


class RetrieveTheCurrentACLEntries(ACLBaseRequest, ACLVerbMixin):
    paths = {
        ACLVerbType.all: '/apps/{appID}/acl',
        ACLVerbType.acl_verb: '/apps/{appID}/acl/{ACLVerb}'
    }

    def __init__(self, api, acl_verb=None):
        super().__init__(api)
        self.acl_verb = acl_verb


class VerifyThePermission(ACLBaseRequest, SubjectTypeMixin):
    paths = {
        SubjectType.user: '/apps/{appID}/acl/{ACLVerb}/UserID:{subjectUserID}',
        SubjectType.group: '/apps/{appID}/acl/{ACLVerb}/GroupID:{subjectGroupID}',
        SubjectType.thing: '/apps/{appID}/acl/{ACLVerb}/ThingID:{subjectThingID}',
    }

    def __init__(self, api, acl_verb, *,
                 subject_user_id=None,
                 subject_group_id=None,
                 subject_thing_id=None):
        super().__init__(api)
        self.acl_verb = acl_verb
        self.subject_user_id = subject_user_id
        self.subject_group_id = subject_group_id
        self.subject_thing_id = subject_thing_id


class GrantThePermission(VerifyThePermission):
    method = 'PUT'


class RevokeThePermission(VerifyThePermission):
    method = 'DELETE'
