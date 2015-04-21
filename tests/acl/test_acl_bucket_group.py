from .base import *  # NOQA


class TestAclBucketGroup(AclGroup):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.target = cls.api.acl.bucket
        cls.ok_subject = ACLSubjectOnBucket.QUERY_OBJECTS_IN_BUCKET
        cls.invalid_subject = ACLSubjectOnScope.CREATE_NEW_TOPIC

    def test_retrieve_the_current_acl_entries(self):
        self.retrieve_the_current_acl_entries(group_id=self.group.group_id, bucket_id=BUCKET_ID)

    def test_verify_the_permission(self):
        self.verify_the_permission(group_id=self.group.group_id, bucket_id=BUCKET_ID)

    def test_grant_the_permission(self):
        self.grant_the_permission(group_id=self.group.group_id, bucket_id=BUCKET_ID)

    def test_revoke_the_permission(self):
        self.revoke_the_permission(group_id=self.group.group_id, bucket_id=BUCKET_ID)
