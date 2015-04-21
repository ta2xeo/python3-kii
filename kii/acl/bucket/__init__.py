from kii.acl.base import Scope
from kii.acl.bucket import (
    application as ApplicationScope,
    group as GroupScope,
    user as UserScope,
)
from kii.utils import Accessor


class AclOnBucket:
    def __init__(self, api):
        self.application = Scope(api, Accessor(ApplicationScope))
        self.group = Scope(api, Accessor(GroupScope))
        self.user = Scope(api, Accessor(UserScope))
