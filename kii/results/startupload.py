from .base import BaseResult


class StartUploadResult(BaseResult):
    @property
    def upload_id(self):
        return self._result['uploadID']
