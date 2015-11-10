from datetime import datetime, timedelta
import os
import time

import pytest
import requests

from kii import AccountType, exceptions as exc, results as rs
from kii.data import BucketType, clauses as cl

from tests.conf import (
    get_env,
    get_api_with_test_user,
    cleanup,
)


GROUP_NAME = 'test_group'
BUCKET_ID = 'test_bucket'


class TestApplicationUpload:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        cleanup()
        self.api = get_api_with_test_user()
        self.scope = self.api.data.application
        self.create_an_object()

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        try:
            self.scope.delete_a_bucket(BUCKET_ID)
        except exc.KiiBucketNotFoundError:
            pass
        cleanup()

    def create_an_object(self):
        self.obj = self.scope(BUCKET_ID).create_an_object({
            'int key': 1,
            'str key': 'this is string',
            'dict key': {
                'nest': 'nest value',
            },
            'list key': [1, 2, 3],
        })

    def test_upload_body_and_committed(self):
        b = self.api.data.application(BUCKET_ID)
        r = b.start_uploading_an_object_body(self.obj._id)
        assert r
        assert isinstance(r.upload_id, str)

        filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'test.mp4')
        MEGA = 1024 * 1024

        with open(filepath, 'rb') as f:
            filesize = os.fstat(f.fileno()).st_size
            size = 0
            start = 0
            end = MEGA
            while True:
                # last
                if end >= filesize:
                    end = filesize - 1

                size = end - start + 1

                body = f.read(size)
                b.upload_the_given_object_data(self.obj._id, r.upload_id, body,
                                               'video/mp4', start, end, filesize)

                if end + 1 >= filesize:
                    break

                start = end + 1
                end = start + MEGA

            b.set_the_object_body_upload_status_to_committed(self.obj._id, r.upload_id)

    def test_upload_body_cancel(self):
        b = self.api.data.application(BUCKET_ID)
        r = b.start_uploading_an_object_body(self.obj._id)
        assert r
        assert isinstance(r.upload_id, str)

        filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'test.mp4')
        MEGA = 1024 * 1024

        with open(filepath, 'rb') as f:
            filesize = os.fstat(f.fileno()).st_size
            size = 0
            start = 0
            end = MEGA
            first = True
            while True:
                # last
                if end >= filesize:
                    end = filesize - 1

                size = end - start + 1

                body = f.read(size)

                if first:
                    b.upload_the_given_object_data(self.obj._id, r.upload_id, body,
                                                   'video/mp4', start, end, filesize)
                else:
                    with pytest.raises(exc.KiiObjectBodyUploadNotFoundError):
                        b.upload_the_given_object_data(self.obj._id, r.upload_id, body,
                                                       'video/mp4', start, end, filesize)

                if end + 1 >= filesize:
                    break

                start = end + 1
                end = start + MEGA

                if first:
                    b.set_the_object_body_upload_status_to_cancelled(self.obj._id, r.upload_id)
                else:
                    with pytest.raises(exc.KiiObjectBodyUploadNotFoundError):
                        b.set_the_object_body_upload_status_to_cancelled(self.obj._id, r.upload_id)

                first = False

    def test_get_upload_metadata(self):
        b = self.api.data.application(BUCKET_ID)
        r = b.start_uploading_an_object_body(self.obj._id)
        assert r
        assert isinstance(r.upload_id, str)

        response = b.get_the_upload_metadata(self.obj._id, r.upload_id)
        assert response is not None

        b.set_the_object_body_upload_status_to_cancelled(self.obj._id, r.upload_id)

        with pytest.raises(exc.KiiObjectBodyUploadNotFoundException):
            b.get_the_upload_metadata(self.obj._id, r.upload_id)

    def test_upload_body_multiple_pieces(self):
        b = self.api.data.application(BUCKET_ID)

        filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'test.mp4')

        with open(filepath, 'rb') as f:
            r = b.upload_body_multiple_pieces(self.obj._id, f.read(), 'video/mp4')
            assert r is True

    def test_upload_body_multiple_pieces2(self):
        b = self.api.data.application(BUCKET_ID)

        filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'test.mp4')

        with open(filepath, 'rb') as f:
            r = self.obj.upload_body_multiple_pieces(f.read(), 'video/mp4')
            assert r is True
