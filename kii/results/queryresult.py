import json

from .base import BaseResult
from .object import ObjectResult


class QueryResult(BaseResult):
    def __init__(self, request_helper, response=None):
        super().__init__(request_helper, response)
        self._total_items = None

    @property
    def total_items(self):
        if self._total_items is None:
            self._total_items = list(self.__iter__())
        return self._total_items

    def __len__(self):
        return len(self.total_items)

    def __getitem__(self, key):
        return self.total_items[key]

    def __setitem__(self, key, val):
        self.total_items[key] = val

    def __delitem__(self, key):
        self.total_items.pop(key)

    def __bool__(self):
        return bool(self.total_items)

    def pop(self, index=None):
        if index is None:
            return self.total_items.pop()
        else:
            return self.total_items.pop(index)

    def __iter__(self):
        if self._total_items is not None:
            for item in self._total_items:
                yield item
            return

        count = -self.request_helper._offset
        for item in self._items:
            count += 1
            if count <= 0:
                continue
            if self.request_helper._limit and count > self.request_helper._limit:
                return
            yield item

        while self.next_pagination_key:
            if self.request_helper._limit and count >= self.request_helper._limit:
                return

            helper = self.request_helper.clone()
            result = helper.pagination_key(self.next_pagination_key).request()

            for item in result._items:
                count += 1
                if count <= 0:
                    continue

                if self.request_helper._limit and count > self.request_helper._limit:
                    return

                yield item

            self.next_pagination_key = result.next_pagination_key

    def json(self):
        return [item.json() for item in self]

    def __str__(self):
        return json.dumps(self.json())

    def set_result(self, result):
        self._items = []
        if isinstance(result['results'], list):
            self._items.extend([
                ObjectResult(self.request_helper,
                             self.response).set_result(r) for r in result['results']
            ])
        else:
            self._items.append(ObjectResult(self.request_helper,
                                            self.response).set_result(result['results']))

        self.next_pagination_key = result.get('nextPaginationKey', None)
        self.query_description = result.get('queryDescription', None)
