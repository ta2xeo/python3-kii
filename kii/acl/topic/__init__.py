from kii.acl.base import Scope
from kii.acl.topic import application as ApplicationScope
from kii.utils import Accessor


class AclOnTopic:
    def __init__(self, api):
        self.application = Scope(api, Accessor(ApplicationScope))
