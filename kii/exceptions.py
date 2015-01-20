class DummyResponse:
    def __init__(self):
        self.status_code = 500
        self.text = {
            'errorCode': 'INTERNAL_ERROR',
        }

    def json(self):
        return self.text


class KiiAPIError(Exception):
    default_message = 'internal error occurred.'

    def __init__(self, error_message=None, response=None):
        if response is None:
            response = DummyResponse()

        self.response = response
        self.status_code = response.status_code
        obj = KiiAPIError.response_json(response)
        message = obj.pop('message', self.default_message)
        self.__dict__.update(obj)

        if error_message is not None:
            message = error_message

        self.message = '[{0}] [{1}] {2}'.format(
            self.status_code,
            self.error_code,
            message,
        )
        super().__init__(self.message)

    @classmethod
    def response_json(cls, response):
        return response.text and response.json() or {}

    @classmethod
    def error_code_from_response(cls, response):
        error = cls.response_json(response).get('errorCode')
        if error:
            return error

        content_type = response.headers['Content-Type']

        if response.text == '{}' and content_type == 'application/json':
            error = {
                401: 'UNAUTHORIZED',
            }.get(response.status_code)
            if error:
                return error

        kii_error = content_type.split(';')[0].split('+')[0].split('.')[-1]
        return kii_error

    @property
    def error_code(self):
        try:
            return self.errorCode
        except AttributeError:
            return KiiAPIError.error_code_from_response(self.response)

    @classmethod
    def distribute_error(cls, response):
        error_code = cls.error_code_from_response(response)
        error_cls = {
            'ACCOUNT_TYPE_NOT_SUPPORTED': KiiAccountTypeNotSupportedError,
            'BUCKET_NOT_FOUND': KiiBucketNotFoundError,
            'GROUP_NOT_FOUND': KiiGroupNotFoundError,
            'invalid_grant': KiiInvalidGrantError,
            'INVALID_INPUT_DATA': KiiInvalidInputDataError,
            'METHOD_NOT_ALLOWED': KiiMethodNotAllowedError,
            'NOT_FOUND': KiiNotFoundError,
            'OBJECT_BODY_NOT_FOUND': KiiObjectBodyNotFoundError,
            'ObjectBodyNotFoundException': KiiObjectBodyNotFoundError,
            'OBJECT_NOT_FOUND': KiiObjectNotFoundError,
            'OBJECT_VERSION_IS_STALE': KiiObjectVersionIsStaleError,
            'PASSWORD_TOO_SHORT': KiiPasswordTooShortError,
            'QUERY_NOT_SUPPORTED': KiiQueryNotSupportedError,
            'UNAUTHORIZED': KiiUnauthorizedError,
            'USER_ALREADY_EXISTS': KiiUserAlreadyExistsError,
            'USER_NOT_FOUND': KiiUserNotFoundError,
            'WRONG_TOKEN': KiiWrongTokenError,
        }.get(error_code, KiiNotImplementedError)
        return error_cls(response=response)


# INTERNAL Errors
class KiiInternvalAPIError(KiiAPIError):
    default_message = 'kii internal api error'
    def __init__(self, msg=None):
        if msg is None:
            msg = self.default_message
        super().__init__(msg)


class KiiHasNotPropertyError(KiiInternvalAPIError):
    default_message = 'object has not property'


class KiiHasNotAccessTokenError(KiiInternvalAPIError):
    default_message = 'has not access token'


class KiiHasNotPropertyError(KiiInternvalAPIError):
    default_message = 'object has not property'


class KiiIllegalAccessError(KiiInternvalAPIError):
    default_message = 'illegal access error'


class KiiInvalidAccountTypeError(KiiInternvalAPIError):
    default_message = 'invalid account type'


class KiiInvalidBucketIdError(KiiInternvalAPIError):
    default_message = 'bucket id is invalid'


class KiiInvalidBucketScopeError(KiiInternvalAPIError):
    default_message = 'bucket scope is invalid'


class KiiInvalidClauseError(KiiInternvalAPIError):
    default_message = 'invalid clause. use clause class object'


class KiiInvalidExpirationError(KiiInternvalAPIError):
    default_message = 'invalid expiration error'


class KiiInvalidGroupIdError(KiiInternvalAPIError):
    default_message = 'group id is invalid'


class KiiInvalidTypeError(KiiInternvalAPIError):
    default_message = 'invalid type error'


class KiiMultipleResultsFoundError(KiiInternvalAPIError):
    default_message = 'multiple results found error'


class KiiUserHasNotAccessTokenError(KiiHasNotPropertyError):
    default_message = 'user has not access token'


# REST API Errors
class KiiAccountTypeNotSupportedError(KiiAPIError):
    pass


class KiiBucketNotFoundError(KiiAPIError):
    pass


class KiiGroupNotFoundError(KiiAPIError):
    pass


class KiiInvalidBucketError(KiiAPIError):
    pass


class KiiInvalidGrantError(KiiAPIError):
    pass


class KiiInvalidInputDataError(KiiAPIError):
    pass


class KiiMethodNotAllowedError(KiiAPIError):
    pass


class KiiNotFoundError(KiiAPIError):
    default_message = 'not found error.'


class KiiNotImplementedError(KiiAPIError):
    default_message = 'not implemented error'


class KiiObjectBodyNotFoundError(KiiAPIError):
    pass


class KiiObjectNotFoundError(KiiAPIError):
    default_message = 'object not found error'


class KiiObjectVersionIsStaleError(KiiAPIError):
    pass


class KiiPasswordTooShortError(KiiAPIError):
    pass


class KiiQueryNotSupportedError(KiiAPIError):
    pass


class KiiUnauthorizedError(KiiAPIError):
    pass


class KiiUserAlreadyExistsError(KiiAPIError):
    pass


class KiiUserNotFoundError(KiiAPIError):
    pass


class KiiWrongTokenError(KiiAPIError):
    pass
