from .group import GroupResult


class GroupInformationResult(GroupResult):
    @property
    def name(self):
        return self._result['name']

    @property
    def owner(self):
        return self._result['owner']
