from .group import GroupResult


class GroupCreationResult(GroupResult):
    @property
    def not_found_users(self):
        return self._result['notFoundUsers']

    @property
    def notFoundUsers(self):
        """
        synonym
        """
        return self.not_found_users
