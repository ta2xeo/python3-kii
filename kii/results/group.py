from .base import BaseResult


class GroupResult(BaseResult):
    @property
    def group_id(self):
        return self._result['groupID']

    @property
    def groupID(self):
        """
        synonym
        """
        return self.group_id
