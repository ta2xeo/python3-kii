import pytest

from kii import exceptions as exc
from kii.acl import *  # NOQA
from kii.users import AccountType

from ..conf import (
    get_api_with_test_user,
    get_admin_api,
    cleanup,
)


GROUP_NAME = 'test_group'
BUCKET_ID = 'test_bucket'


class AclApp:
    @classmethod
    def setup_class(cls):
        cleanup()
        cls.api = get_admin_api()
        cls.user_api = get_api_with_test_user()

        user = cls.user_api.user.retrieve_user_data()
        assert user

        cls.group = cls.user_api.group.create_a_group(GROUP_NAME, user)
        assert cls.group

        cls.target = None
        cls.ok_subject = None
        cls.ng_subject = None
        cls.invalid_subject = None

    @classmethod
    def teardown_class(cls):
        cleanup()
        cls.api.group.delete_a_group(cls.group.group_id)

    def retrieve_the_current_acl_entries(self, *args, **kwargs):
        entries = self.target.application.retrieve_the_current_acl_entries(*args, **kwargs)
        assert entries

        entries = self.target.application.retrieve_the_current_acl_entries(
            *args, acl_verb=self.ok_subject, **kwargs)
        assert entries

        if self.ng_subject is not None:
            entries = self.target.application.retrieve_the_current_acl_entries(
                acl_verb=self.ng_subject, *args, **kwargs)
            assert not entries

        with pytest.raises(exc.KiiInvalidTypeError):
            self.target.application.retrieve_the_current_acl_entries(
                acl_verb=self.invalid_subject, *args, **kwargs)

    def verify_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiGroupNotFoundError):
            self.target.application.verify_the_permission(
                acl_verb=self.ok_subject, subject_group_id=GROUP_NAME, *args, **kwargs)

        with pytest.raises(exc.KiiAclNotFoundError):
            self.target.application.verify_the_permission(
                *args,
                acl_verb=self.ok_subject,
                subject_group_id=self.group.group_id,
                **kwargs)

        if self.ng_subject is not None:
            with pytest.raises(exc.KiiAclNotFoundError):
                self.target.application.verify_the_permission(
                    *args,
                    acl_verb=self.ng_subject,
                    subject_group_id=self.group.group_id,
                    **kwargs)

    def grant_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiGroupNotFoundError):
            self.target.application.grant_the_permission(
                *args, acl_verb=self.ok_subject, subject_group_id=GROUP_NAME, **kwargs)

        self.target.application.grant_the_permission(
            *args, acl_verb=self.ok_subject,
            subject_group_id=self.group.group_id, **kwargs)

    def revoke_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiAclNotFoundError):
            self.target.application.revoke_the_permission(
                *args, acl_verb=self.ok_subject, subject_group_id=GROUP_NAME, **kwargs)

        self.target.application.revoke_the_permission(
            *args, acl_verb=self.ok_subject, subject_group_id=self.group.group_id, **kwargs)


class AclGroup:
    @classmethod
    def setup_class(cls):
        cleanup()
        cls.api = get_admin_api()
        cls.user_api = get_api_with_test_user()

        user = cls.user_api.user.retrieve_user_data()
        assert user

        cls.group = cls.user_api.group.create_a_group(GROUP_NAME, user)
        assert cls.group

        cls.target = None
        cls.ok_subject = None
        cls.ng_subject = None
        cls.invalid_subject = None

        cls.obj = cls.api.data.group(cls.group.group_id, BUCKET_ID).create_an_object({
            'a': 1
        })

    @classmethod
    def teardown_class(cls):
        cleanup()
        cls.api.data.group.delete_a_bucket(cls.group.group_id, BUCKET_ID)
        cls.api.group.delete_a_group(cls.group.group_id)

    def retrieve_the_current_acl_entries(self, *args, **kwargs):
        entries = self.target.group.retrieve_the_current_acl_entries(*args, **kwargs)
        assert entries

        entries = self.target.group.retrieve_the_current_acl_entries(
            *args, acl_verb=self.ok_subject, **kwargs)
        assert entries

        if self.ng_subject is not None:
            entries = self.target.group.retrieve_the_current_acl_entries(
                acl_verb=self.ng_subject, *args, **kwargs)
            assert not entries

        with pytest.raises(exc.KiiInvalidTypeError):
            self.target.group.retrieve_the_current_acl_entries(
                acl_verb=self.invalid_subject, *args, **kwargs)

    def verify_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiGroupNotFoundError):
            self.target.group.verify_the_permission(
                acl_verb=self.ok_subject, subject_group_id=GROUP_NAME, *args, **kwargs)

        self.target.group.verify_the_permission(
            *args,
            acl_verb=self.ok_subject,
            subject_group_id=self.group.group_id,
            **kwargs)

        if self.ng_subject is not None:
            with pytest.raises(exc.KiiAclNotFoundError):
                self.target.group.verify_the_permission(
                    *args,
                    acl_verb=self.ng_subject,
                    subject_group_id=self.group.group_id,
                    **kwargs)

    def grant_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiGroupNotFoundError):
            self.target.group.grant_the_permission(
                *args, acl_verb=self.ok_subject, subject_group_id=GROUP_NAME, **kwargs)

        with pytest.raises(exc.KiiAclAlreadyExistsError):
            self.target.group.grant_the_permission(
                *args, acl_verb=self.ok_subject,
                subject_group_id=self.group.group_id, **kwargs)

    def revoke_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiAclNotFoundError):
            self.target.group.revoke_the_permission(
                *args, acl_verb=self.ok_subject, subject_group_id=GROUP_NAME, **kwargs)

        self.target.group.revoke_the_permission(
            *args, acl_verb=self.ok_subject, subject_group_id=self.group.group_id, **kwargs)


class AclUser:
    @classmethod
    def setup_class(cls):
        cleanup()
        cls.api = get_admin_api()
        cls.user_api = get_api_with_test_user()

        cls.user = cls.user_api.user.retrieve_user_data()
        assert cls.user

        cls.target = None
        cls.target_by_admin = None
        cls.ok_subject = None
        cls.ng_subject = None
        cls.invalid_subject = None

        cls.obj = cls.user_api.data.user(BUCKET_ID).create_an_object({
            'a': 1
        })

        # dummy user
        email = 'dummy@example.com'
        try:
            cls.dummy = cls.api.user.retrieve_user_data(account_type=AccountType.email.value,
                                                        address=email)
        except exc.KiiUserNotFoundError:
            cls.dummy = cls.api.user.create_a_user(email_address=email, password='password')

    @classmethod
    def teardown_class(cls):
        cls.user_api.data.user.delete_a_bucket(BUCKET_ID)
        cleanup()

        cls.api.user.delete_a_user(user_id=cls.dummy.user_id)

    def retrieve_the_current_acl_entries(self, *args, **kwargs):
        entries = self.target.user.retrieve_the_current_acl_entries(*args, **kwargs)
        assert entries

        entries = self.target.user.retrieve_the_current_acl_entries(
            *args, acl_verb=self.ok_subject, **kwargs)
        assert entries

        if self.ng_subject is not None:
            entries = self.target.user.retrieve_the_current_acl_entries(
                acl_verb=self.ng_subject, *args, **kwargs)
            assert not entries

        with pytest.raises(exc.KiiInvalidTypeError):
            self.target.user.retrieve_the_current_acl_entries(
                acl_verb=self.invalid_subject, *args, **kwargs)

    def verify_the_permission(self, *args, **kwargs):
        self.target.user.verify_the_permission(
            *args,
            acl_verb=self.ok_subject,
            subject_user_id=self.user.user_id,
            **kwargs)

        if self.ng_subject is not None:
            with pytest.raises(exc.KiiAclNotFoundError):
                self.target.user.verify_the_permission(
                    *args,
                    acl_verb=self.ng_subject,
                    subject_user_id=self.user.user_id,
                    **kwargs)

    def grant_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiAclAlreadyExistsError):
            self.target.user.grant_the_permission(
                *args, acl_verb=self.ok_subject,
                subject_user_id=self.user.user_id, **kwargs)

    def revoke_the_permission(self, *args, **kwargs):
        with pytest.raises(exc.KiiOperationNotAllowedError):
            self.target.user.revoke_the_permission(
                *args, acl_verb=self.ok_subject, subject_user_id=self.user.user_id, **kwargs)

        self.target.user.grant_the_permission(
            *args, acl_verb=self.ok_subject,
            subject_user_id=self.dummy.user_id, **kwargs)

        self.target_by_admin.user.revoke_the_permission(
            *args, acl_verb=self.ok_subject, subject_user_id=self.dummy.user_id, **kwargs)
