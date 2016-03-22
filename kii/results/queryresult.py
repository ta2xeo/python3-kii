import json

from .base import BaseResult
from .object import ObjectResult


class QueryResult(BaseResult):
    def __init__(self, request_helper, response=None):
        super().__init__(request_helper, response)
        self._cache_results = []
        self._finished = False

    @property
    def all_items(self):
        if not self._finished:
            self._cache_results = list(self.__iter__())
            self._finished = True
        return self._cache_results

    def __len__(self):
        return len(self.all_items)

    def __getitem__(self, key):
        return self.all_items[key]

    def __setitem__(self, key, val):
        self.all_items[key] = val

    def __delitem__(self, key):
        self.all_items.pop(key)

    def __bool__(self):
        if not self._finished:
            b = bool(self._cache_results)
            if b:
                return True
        return bool(self.all_items)

    def pop(self, index=None):
        if index is None:
            return self.all_items.pop()
        else:
            return self.all_items.pop(index)

    def __iter__(self):
        if self._finished:
            for item in self._cache_results:
                yield item
            return

        for item in self._cache_results[:]:
            yield item

        cache_offset = len(self._cache_results)
        count = -self.request_helper._offset
        for item in self._items[cache_offset:]:
            count += 1
            if count <= 0:
                continue
            if self.request_helper._limit and count > self.request_helper._limit:
                self._finished = True
                return

            self._cache_results.append(item)
            yield item

        while self.next_pagination_key:
            if self.request_helper._limit and count >= self.request_helper._limit:
                self._finished = True
                return

            helper = self.request_helper.clone()
            result = helper.pagination_key(self.next_pagination_key).request()

            for item in result._items:
                count += 1
                if count <= 0:
                    continue

                if self.request_helper._limit and count > self.request_helper._limit:
                    self._finished = True
                    return

                self._cache_results.append(item)
                yield item

            self.next_pagination_key = result.next_pagination_key

        self._finished = True

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
