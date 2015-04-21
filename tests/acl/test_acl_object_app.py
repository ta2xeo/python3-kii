from .base import *  # NOQA


class TestAclObjectApp(AclApp):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.object = cls.api.data.application(BUCKET_ID).create_an_object({})
        cls.target = cls.api.acl.object
        cls.ok_subject = ACLSubjectOnObject.WRITE_EXISTING_OBJECT
        cls.invalid_subject = ACLSubjectOnScope.CREATE_NEW_TOPIC

    @classmethod
    def teardown_class(cls):
        super().teardown_class()
        cls.api.data.application.delete_a_bucket(BUCKET_ID)

    def test_retrieve_the_current_acl_entries(self):
        self.retrieve_the_current_acl_entries(bucket_id=BUCKET_ID, object_id=self.object.id)

    def test_verify_the_permission(self):
        self.verify_the_permission(bucket_id=BUCKET_ID, object_id=self.object.id)

    def test_grant_the_permission(self):
        self.grant_the_permission(bucket_id=BUCKET_ID, object_id=self.object.id)

    def test_revoke_the_permission(self):
        self.revoke_the_permission(bucket_id=BUCKET_ID, object_id=self.object.id)
