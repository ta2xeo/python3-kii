from .base import *  # NOQA


class TestAclScopeApp(AclApp):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.target = cls.api.acl.scope
        cls.ok_subject = ACLSubjectOnScope.CREATE_NEW_BUCKET
        cls.ng_subject = ACLSubjectOnScope.CREATE_NEW_TOPIC
        cls.invalid_subject = ACLSubjectOnBucket.QUERY_OBJECTS_IN_BUCKET

    def test_retrieve_the_current_acl_entries(self):
        self.retrieve_the_current_acl_entries()

    def test_verify_the_permission(self):
        self.verify_the_permission()

    def test_grant_the_permission(self):
        self.grant_the_permission()

    def test_revoke_the_permission(self):
        self.revoke_the_permission()
