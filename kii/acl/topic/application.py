from kii.acl.base import (
    ACLBaseRequest, ACLVerbMixin, ACLSubjectOnTopic, ACLVerbType,
    SubjectType, SubjectTypeMixin,
)


class TopicArgsMixin:
    def format_args(self):
        args = self._format_args()
        args['topicID'] = self.topic_id
        return args


class RetrieveTheCurrentACLEntries(TopicArgsMixin, ACLVerbMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnTopic

    def __init__(self, api, topic_id, acl_verb=None):
        super().__init__(api)
        self.topic_id = topic_id
        self.acl_verb = acl_verb

    def paths(self):
        return {
            ACLVerbType.all: '/apps/{appID}/topics/{topicID}/acl',
            ACLVerbType.acl_verb: '/apps/{appID}/topics/{topicID}/acl/{ACLVerb}',
        }


class VerifyThePermission(TopicArgsMixin, SubjectTypeMixin, ACLBaseRequest):
    ACLSubject = ACLSubjectOnTopic
    paths = {
        SubjectType.user: '/apps/{appID}/topics/{topicID}/acl/{ACLVerb}/UserID:{subjectUserID}',
        SubjectType.group: '/apps/{appID}/topics/{topicID}/acl/{ACLVerb}/GroupID:{subjectGroupID}',
        SubjectType.thing: '/apps/{appID}/topics/{topicID}/acl/{ACLVerb}/ThingID:{subjectThingID}',
    }

    def __init__(self, api, topic_id, acl_verb, *,
                 subject_user_id=None,
                 subject_group_id=None,
                 subject_thing_id=None):
        super().__init__(api)
        self.topic_id = topic_id
        self.acl_verb = acl_verb
        self.subject_user_id = subject_user_id
        self.subject_group_id = subject_group_id
        self.subject_thing_id = subject_thing_id


class GrantThePermission(VerifyThePermission):
    method = 'PUT'


class RevokeThePermission(VerifyThePermission):
    method = 'DELETE'
