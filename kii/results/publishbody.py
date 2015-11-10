from .base import BaseResult


class PublishBodyResult(BaseResult):
    def set_result(self, result):
        super().set_result(result)

    @property
    def publication_id(self):
        return self._result['publicationID']

    @property
    def publicationID(self):
        """
        synonym
        """
        return self.publication_id

    @property
    def url(self):
        return self._result['url']
