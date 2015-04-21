from kii.acl.enums import *  # NOQA
from kii.acl.scope import AclOnScope
from kii.acl.bucket import AclOnBucket
from kii.acl.object import AclOnObject
from kii.acl.topic import AclOnTopic


class AclManagement:
    def __init__(self, api):
        self.scope = AclOnScope(api)
        self.bucket = AclOnBucket(api)
        self.object = AclOnObject(api)
        self.topic = AclOnTopic(api)
