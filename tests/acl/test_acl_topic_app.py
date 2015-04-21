from .base import *  # NOQA


TOPIC_ID = 'test_topic'


class TestAclTopicApp(AclApp):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.object = cls.api.data.application(BUCKET_ID).create_an_object({})
        cls.target = cls.api.acl.topic
        cls.ok_subject = ACLSubjectOnTopic.SUBSCRIBE_TO_TOPIC
        cls.invalid_subject = ACLSubjectOnScope.CREATE_NEW_TOPIC

    @classmethod
    def teardown_class(cls):
        super().teardown_class()
        cls.api.data.application.delete_a_bucket(BUCKET_ID)

    # def test_retrieve_the_current_acl_entries(self):
    #     self.retrieve_the_current_acl_entries(topic_id=TOPIC_ID)

    # def test_verify_the_permission(self):
    #     self.verify_the_permission(topic_id=TOPIC_ID)

    # def test_grant_the_permission(self):
    #     self.grant_the_permission(topic_id=TOPIC_ID)

    # def test_revoke_the_permission(self):
    #     self.revoke_the_permission(topic_id=TOPIC_ID)
