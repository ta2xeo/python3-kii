# only python3
import json
from collections.abc import MutableMapping
from datetime import datetime

from kii.exceptions import (
    KiiHasNotPropertyError,
    KiiUserHasNotAccessTokenError,
)


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

    def __str__(self):
        return '{0} RESULTS {1}'.format(repr(self), json.dumps(self.json()))

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


class BucketResult(BaseResult):
    @property
    def bucket_type(self):
        return self._result['bucketType']

    @property
    def bucketType(self):
        return self.bucket_type

    @property
    def size(self):
        return self._result['size']


class BodyResult(BaseResult):
    def __init__(self, request_helper, response):
        self.request_helper = request_helper
        self.response = response
        self.set_result(response.content)

    def __str__(self):
        return self.body.decode('utf-8')

    @property
    def body(self):
        return self._result


class CreateResult(ObjectResult):
    def set_result(self, result):
        super().set_result(result)

    @property
    def _id(self):
        return self.object_id

    @property
    def id(self):
        return self._id

    @property
    def object_id(self):
        return self._result['objectID']

    @property
    def objectID(self):
        return self.object_id

    @property
    def created_at(self):
        return datetime.fromtimestamp(self._result['createdAt'] / 1000)

    @property
    def createdAt(self):
        return self.created_at

    @property
    def data_type(self):
        return self._result['dataType']

    @property
    def dataType(self):
        return self.data_type


class DeleteResult(BaseResult):
    pass


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


class QueryResult(BaseResult):
    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, val):
        self._items[key] = val

    def __delitem__(self, key):
        self._items.pop(key)

    def __bool__(self):
        return bool(self._items)

    def pop(self, index=None):
        if index is None:
            return self._items.pop()
        else:
            return self._items.pop(index)

    def __iter__(self):
        for item in self._items:
            yield item

        raise StopIteration

    def json(self):
        return [item.json() for item in self]

    def set_result(self, result):
        self._items = []
        if isinstance(result['results'], list):
            self._items.extend([ObjectResult(self.request_helper, self.response).set_result(r) for r in result['results']])
        else:
            self._items.append(ObjectResult(self.request_helper, self.response).set_result(result['results']))

        self.next_pagination_key = result.get('nextPaginationKey', None)
        self.query_description = result.get('queryDescription', None)

        if self.next_pagination_key:
            helper = self.request_helper.clone()
            helper.pagination_key = self.next_pagination_key
            if helper.best_effort_limit is not None:
                helper.best_effort_limit -= len(self)

            if helper.best_effort_limit is None or helper.best_effort_limit > 0:
                result = helper.request()
                self.next_pagination_key = result.next_pagination_key
                self.query_description = result.query_description
                self._items.extend(list(result))


class TokenResult(BaseResult):
    @property
    def access_token(self):
        return self._result['access_token']

    @property
    def expires_in(self):
        return self._result['expires_in']

    @property
    def id(self):
        return self._result['id']

    @property
    def token_type(self):
        return self._result['token_type']


class UpdateResult(ObjectResult):
    pass


class UserResult(BaseResult):
    @property
    def _access_token(self):
        try:
            return self._result['_accessToken']
        except KeyError as e:
            raise KiiUserHasNotAccessTokenError from e

    @property
    def _accessToken(self):
        """
        synonym
        """
        return self._access_token

    @property
    def _disabled(self):
        return self._result['_disabled']

    @property
    def _has_password(self):
        return self._result['_hasPassword']

    @property
    def _hasPassword(self):
        """
        synonym
        """
        return self._has_password

    @property
    def access_token(self):
        return self._access_token

    @property
    def country(self):
        try:
            return self._result['country']
        except KeyError as e:
            raise KiiHasNotPropertyError('this user has not country property') from e

    @property
    def display_name(self):
        return self._result['displayName']

    @property
    def displayName(self):
        """
        synonym
        """
        return self.display_name

    @property
    def email_address(self):
        return self._result['emailAddress']

    @property
    def emailAddress(self):
        """
        synonym
        """
        return self.email_address

    @property
    def email_address_verified(self):
        return self._result['emailAddressVerified']

    @property
    def emailAddressVerified(self):
        """
        synonym
        """
        return self.email_address_verified

    @property
    def internal_user_id(self):
        return self._result['internalUserID']

    @property
    def internalUserID(self):
        """
        synonym
        """
        return self.internal_user_id

    @property
    def locale(self):
        return self._result['locale']

    @property
    def login_name(self):
        return self._result['loginName']

    @property
    def loginName(self):
        """
        synonym
        """
        return self.login_name

    @property
    def phone_number(self):
        return self._result['phoneNumber']

    @property
    def phoneNumber(self):
        """
        synonym
        """
        return self.phone_number

    @property
    def phone_number_verified(self):
        return self._result['phoneNumberVerified']

    @property
    def phoneNumberVerified(self):
        """
        synonym
        """
        return self.phone_number_verified

    @property
    def user_id(self):
        return self._result['userID']

    @property
    def userID(self):
        """
        synonym
        """
        return self.user_id

    def delete(self):
        api = self.api.clone(access_token=self.access_token)
        api.users.delete_a_user()


class GroupResult(BaseResult):
    @property
    def group_id(self):
        return self._result['groupID']

    @property
    def groupID(self):
        """
        synonym
        """
        return self.group_id


class GroupCreationResult(GroupResult):
    @property
    def not_found_users(self):
        return self._result['notFoundUsers']

    @property
    def notFoundUsers(self):
        """
        synonym
        """
        return self.not_found_users


class GroupInformationResult(GroupResult):
    @property
    def name(self):
        return self._result['name']

    @property
    def owner(self):
        return self._result['owner']
