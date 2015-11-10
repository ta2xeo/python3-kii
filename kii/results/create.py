from datetime import datetime

from .object import ObjectResult


class CreateResult(ObjectResult):
    def set_result(self, result):
        super().set_result(result)

    @property
    def _id(self):
        return self.object_id

    @property
    def id(self):
        return self._id

    @property
    def object_id(self):
        return self._result['objectID']

    @property
    def objectID(self):
        return self.object_id

    @property
    def created_at(self):
        return datetime.fromtimestamp(self._result['createdAt'] / 1000)

    @property
    def createdAt(self):
        return self.created_at

    @property
    def data_type(self):
        return self._result['dataType']

    @property
    def dataType(self):
        return self.data_type
