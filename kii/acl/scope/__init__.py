from kii.acl.base import Scope
from kii.acl.scope import application as ApplicationScope
from kii.utils import Accessor


class AclOnScope:
    def __init__(self, api):
        self.application = Scope(api, Accessor(ApplicationScope))
