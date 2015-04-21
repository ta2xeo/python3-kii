from kii import exceptions as exc


class Accessor:
    def __init__(self, scope):
        self.scope = scope

    def __getattr__(self, name):
        try:
            return getattr(self.scope, name)
        except AttributeError as e:
            raise exc.KiiNotImplementedError(
                '{0} is not implemented in {1} scope.'.format(name, self.scope)) from e
