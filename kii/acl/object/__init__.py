from kii.acl.base import Scope
from kii.acl.object import application as ApplicationScope
from kii.utils import Accessor


class AclOnObject:
    def __init__(self, api):
        self.application = Scope(api, Accessor(ApplicationScope))
