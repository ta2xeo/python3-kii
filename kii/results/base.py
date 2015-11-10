import json
from collections.abc import MutableMapping


class BaseResult(MutableMapping):
    def __init__(self, request_helper, response=None):
        self.request_helper = request_helper
        self.response = response
        self.set_result(response.text and response.json())

    def __getitem__(self, key):
        return self._result[key]

    def __setitem__(self, key, val):
        self._result[key] = val

    def __delitem__(self, key):
        del self._result[key]

    def __iter__(self):
        for some in self._result:
            yield some
        raise StopIteration

    def __len__(self):
        return len(self._result)

    def __contains__(self, item):
        return item in self._result

    def __bool__(self):
        return bool(self._result)

    def __repr__(self):
        return '{0} RESULTS {1}'.format(super().__repr__(), str(self))

    def __str__(self):
        return json.dumps(self._result)

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def bucket_id(self):
        return self.request_helper.bucket_id

    @property
    def api(self):
        return self.request_helper.api

    def json(self):
        if isinstance(self._result, list):
            return [r.json() for r in self._result]
        return self._result

    def set_result(self, result):
        self._result = result
