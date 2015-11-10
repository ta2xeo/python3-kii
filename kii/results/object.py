from datetime import datetime

from .base import BaseResult


class ObjectResult(BaseResult):
    """
    for buckets result
    """
    def set_result(self, result):
        super().set_result(result)
        return self

    @property
    def _created(self):
        return datetime.fromtimestamp((self._result['_created']) / 1000)

    @property
    def _id(self):
        return self._result['_id']

    @property
    def _modified(self):
        return datetime.fromtimestamp((self._result['_modified']) / 1000)

    @property
    def _owner(self):
        return self._result['_owner']

    @property
    def _version(self):
        return int(self._result['_version'])

    def refresh(self):
        scope = self.request_helper.scope
        new = scope.retrieve_an_object(self._id)
        return self.set_result(new.json())

    def partially_update(self, params, **kwargs):
        scope = self.request_helper.scope
        return scope.partially_update_an_object(self._id, params, **kwargs)

    def retrieve_body(self, **kwargs):
        scope = self.request_helper.scope
        return scope.retrieve_an_object_body(self._id, **kwargs)

    def add_or_replace_body(self, body, content_type):
        scope = self.request_helper.scope
        return scope.add_or_replace_an_object_body(self._id, body, content_type)

    def verify_body(self):
        scope = self.request_helper.scope
        return scope.verify_the_object_body_existence(self._id)

    def has_body(self):
        scope = self.request_helper.scope
        return scope.has_body(self._id)

    def delete_body(self):
        scope = self.request_helper.scope
        return scope.delete_an_object_body(self._id)

    def publish_body(self, *, expires_at=None, expires_in=None):
        scope = self.request_helper.scope
        return scope.publish_an_object_body(self._id,
                                            expires_at=expires_at,
                                            expires_in=expires_in)
