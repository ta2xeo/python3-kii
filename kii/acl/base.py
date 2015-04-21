from kii import exceptions as exc, results as rs
from kii.acl.enums import *  # NOQA
from kii.enums import UserRequestType
from kii.helpers import RequestHelper


class ACLBaseRequest(RequestHelper):
    method = 'GET'
    result_container = rs.BaseResult
    ACLSubject = ACLSubjectOnScope

    @property
    def acl_verb(self):
        if self._acl_verb is None:
            return None
        return self._acl_verb.value

    @acl_verb.setter
    def acl_verb(self, verb):
        if verb is not None and not isinstance(verb, self.ACLSubject):
            raise exc.KiiInvalidTypeError('specified ACLSubject is invalid. Use {0}'
                                          .format(self.ACLSubject))
        self._acl_verb = verb

    @property
    def api_path(self):
        return self.determine_path().format(**self.format_args())

    @property
    def headers(self):
        headers = super().headers
        if self.access_token:
            headers['Authorization'] = self.authorization

        return headers

    def format_args(self):
        return self._format_args()


class UserRequestTypeMixin:
    @property
    def user_request_type(self):
        from kii.api import KiiAdminAPI

        if self.account_type and self.address:
            return UserRequestType.by_address

        if self.user_id:
            return UserRequestType.by_id

        if isinstance(self.api, KiiAdminAPI):
            raise exc.KiiIllegalAccessError

        return UserRequestType.by_me_literal


class ACLVerbMixin:
    @property
    def verb_type(self):
        if self.acl_verb:
            return ACLVerbType.acl_verb
        return ACLVerbType.all

    def determine_path(self):
        return self.paths[self.verb_type]

    def _format_args(self):
        return {
            ACLVerbType.acl_verb: {
                'appID': self.api.app_id,
                'ACLVerb': self.acl_verb,
            },
            ACLVerbType.all: {
                'appID': self.api.app_id,
            }
        }[self.verb_type]


class UserACLVerbMixin(UserRequestTypeMixin, ACLVerbMixin):
    def determine_path(self):
        return self.paths[self.verb_type][self.user_request_type]


class SubjectTypeMixin:
    @property
    def subject_type(self):
        if hasattr(self, '_subject_type'):
            return self._subject_type

        self._subject_type = None
        if self.subject_user_id:
            self._subject_type = SubjectType.user
        elif self.subject_group_id:
            self._subject_type = SubjectType.group
        elif self.subject_thing_id:
            self._subject_type = SubjectType.thing
        else:
            raise exc.KiiInvalidTypeError
        return self._subject_type

    def determine_path(self):
        return self.paths[self.subject_type]

    def _format_args(self):
        return {
            SubjectType.user: {
                'appID': self.api.app_id,
                'ACLVerb': self.acl_verb,
                'subjectUserID': self.subject_user_id,
            },
            SubjectType.group: {
                'appID': self.api.app_id,
                'ACLVerb': self.acl_verb,
                'subjectGroupID': self.subject_group_id,
            },
            SubjectType.thing: {
                'appID': self.api.app_id,
                'ACLVerb': self.acl_verb,
                'subjectThingID': self.subject_thing_id,
            }
        }[self.subject_type]


class UserSubjectTypeMixin(UserRequestTypeMixin, SubjectTypeMixin):
    def determine_path(self):
        return self.paths[self.subject_type][self.user_request_type]


class Scope:
    def __init__(self, api, scope):
        self.api = api
        self.scope = scope

    def request(self, cls, *args, **kwargs):
        helper = cls(self.api, *args, **kwargs)
        return helper.request()

    def retrieve_the_current_acl_entries(self, *args,
                                         **kwargs):
        return self.request(self.scope.RetrieveTheCurrentACLEntries,
                            *args,
                            **kwargs)

    def verify_the_permission(self, *args,
                              subject_user_id=None,
                              subject_group_id=None,
                              subject_thing_id=None,
                              **kwargs):
        return self.request(self.scope.VerifyThePermission,
                            *args,
                            subject_user_id=subject_user_id,
                            subject_group_id=subject_group_id,
                            subject_thing_id=subject_thing_id,
                            **kwargs)

    def grant_the_permission(self, *args,
                             subject_user_id=None,
                             subject_group_id=None,
                             subject_thing_id=None,
                             **kwargs):
        return self.request(self.scope.GrantThePermission,
                            *args,
                            subject_user_id=subject_user_id,
                            subject_group_id=subject_group_id,
                            subject_thing_id=subject_thing_id,
                            **kwargs)

    def revoke_the_permission(self, *args,
                              subject_user_id=None,
                              subject_group_id=None,
                              subject_thing_id=None,
                              **kwargs):
        return self.request(self.scope.RevokeThePermission,
                            *args,
                            subject_user_id=subject_user_id,
                            subject_group_id=subject_group_id,
                            subject_thing_id=subject_thing_id,
                            **kwargs)
