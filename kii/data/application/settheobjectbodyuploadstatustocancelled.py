from kii import results as rs
from .settheobjectbodyuploadstatustocommitted import SetTheObjectBodyUploadStatusToCommitted


class SetTheObjectBodyUploadStatusToCancelled(SetTheObjectBodyUploadStatusToCommitted):
    @property
    def api_path(self):
        return '/apps/{appID}/buckets/{bucketID}/objects/{objectID}/body/uploads/{uploadID}/status/cancelled'.format(
            appID=self.api.app_id,
            bucketID=self.bucket_id,
            objectID=self.object_id,
            uploadID=self.upload_id)
