from .base import BaseResult


class BucketResult(BaseResult):
    @property
    def bucket_type(self):
        from kii.data import BucketType
        return BucketType(self._result['bucketType'])

    @property
    def bucketType(self):
        return self.bucket_type

    @property
    def size(self):
        return self._result['size']
