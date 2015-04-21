from enum import Enum, unique


@unique
class ACLSubjectOnScope(Enum):
    CREATE_NEW_BUCKET = 'CREATE_NEW_BUCKET'
    CREATE_NEW_TOPIC = 'CREATE_NEW_TOPIC'


@unique
class ACLSubjectOnBucket(Enum):
    QUERY_OBJECTS_IN_BUCKET = 'QUERY_OBJECTS_IN_BUCKET'
    CREATE_OBJECTS_IN_BUCKET = 'CREATE_OBJECTS_IN_BUCKET'
    DROP_BUCKET_WITH_ALL_CONTENT = 'DROP_BUCKET_WITH_ALL_CONTENT'


@unique
class ACLSubjectOnObject(Enum):
    READ_EXISTING_OBJECT = 'READ_EXISTING_OBJECT'
    WRITE_EXISTING_OBJECT = 'WRITE_EXISTING_OBJECT'


@unique
class ACLSubjectOnTopic(Enum):
    SUBSCRIBE_TO_TOPIC = 'SUBSCRIBE_TO_TOPIC'
    SEND_MESSAGE_TO_TOPIC = 'SEND_MESSAGE_TO_TOPIC'


@unique
class ACLVerbType(Enum):
    all = 1
    acl_verb = 2


@unique
class SubjectType(Enum):
    user = 1
    group = 2
    thing = 3


class UserGrant(Enum):
    ANONYMOUS_USER = 'ANONYMOUS_USER'
    ANONYMOUS = ANONYMOUS_USER  # synonym
    ANY_AUTHENTICATED_USER = 'ANY_AUTHENTICATED_USER'
    ANY_AUTHENTICATED = ANY_AUTHENTICATED_USER  # synonym
