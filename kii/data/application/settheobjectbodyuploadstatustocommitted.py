from kii import results as rs
from kii.helpers import BucketsHelper


class SetTheObjectBodyUploadStatusToCommitted(BucketsHelper):
    method = 'POST'
    result_container = rs.BaseResult

    def __init__(self, scope, object_id, upload_id):
        super().__init__(scope)
        self.object_id = object_id
        self.upload_id = upload_id

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body/uploads/{uploadID}/status/committed'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id,
            uploadID=self.upload_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Authorization'] = self.authorization
        return headers

    def request(self):
        super().request(data='')
