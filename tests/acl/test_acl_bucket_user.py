from .base import *  # NOQA


class TestAclBucketUser(AclUser):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.target = cls.user_api.acl.bucket
        cls.target_by_admin = cls.api.acl.bucket
        cls.ok_subject = ACLSubjectOnBucket.QUERY_OBJECTS_IN_BUCKET
        cls.invalid_subject = ACLSubjectOnScope.CREATE_NEW_TOPIC

    def test_retrieve_the_current_acl_entries(self):
        self.retrieve_the_current_acl_entries(bucket_id=BUCKET_ID)

    def test_verify_the_permission(self):
        self.verify_the_permission(bucket_id=BUCKET_ID)

    def test_grant_the_permission(self):
        self.grant_the_permission(bucket_id=BUCKET_ID)

    def test_revoke_the_permission(self):
        self.revoke_the_permission(bucket_id=BUCKET_ID, user_id=self.user.user_id)
