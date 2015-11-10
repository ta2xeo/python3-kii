from kii import results as rs
from kii.helpers import BucketsHelper


class StartUploadingAnObjectBody(BucketsHelper):
    method = 'POST'
    result_container = rs.StartUploadResult

    def __init__(self, scope, object_id):
        super().__init__(scope)
        self.object_id = object_id

    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body/uploads'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id)

    @property
    def headers(self):
        headers = super().headers
        headers['Authorization'] = self.authorization
        headers['Content-Type'] = 'application/vnd.kii.StartObjectBodyUploadRequest+json'
        return headers

    def request(self):
        return super().request(json={})
