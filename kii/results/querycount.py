from .base import BaseResult


class QueryCountResult(BaseResult):
    @property
    def count(self):
        return self._result['aggregations']['count_field']
