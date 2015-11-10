from kii import results as rs
from kii.helpers import BucketsHelper


class UploadTheGivenObjectData(BucketsHelper):
    method = 'PUT'
    result_container = rs.BaseResult

    def __init__(self, scope, object_id, upload_id, body, content_type,
                 start_byte, end_byte, total_byte):
        super().__init__(scope)
        self.object_id = object_id
        self.upload_id = upload_id
        self.body = body
        self.content_type = content_type
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.total_byte = total_byte

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body/uploads/{uploadID}/data'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id,
            uploadID=self.upload_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Authorization'] = self.authorization
        headers['Content-Range'] = 'bytes={start}-{end}/{total}'.format(start=self.start_byte,
                                                                        end=self.end_byte,
                                                                        total=self.total_byte)
        headers['Content-Type'] = self.content_type
        return headers

    def request(self):
        super().request(data=self.body)
