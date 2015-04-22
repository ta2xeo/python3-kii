Overview
=========================

Python3-kii is a python library for kii cloud REST API.
This library is implemented functions along the official documentation as far as possible.
But, it is not fully implemented functions.


Requirements
=========================

* "python3-kii" works only under python3.4 or later.
* "Python 2.X" and "Python 3.3 or older" is not supported.


Sample usage
=========================

    >>> from kii import KiiAPI

create a user

    >>> api = KiiAPI(app_id, app_key)
    >>> api.user.create_a_user(login_name='test', password='pass1234')


create a object

    >>> api.data.application('bucket_name').create_an_object({'key': 'value'})
    >>> api.data.group('group_id', 'bucket_name').create_an_object({'key': 'value'})
    >>> api.data.user('bucket_name', user_id=user_id).create_an_object({'key': 'value'})


query for objects

    >>> from kii.data.clauses import *
    >>> clause = AndClause(EqualClause('index', 3), RangeClause('age').ge(20))
    >>> str(clause)
    '<Clause Object:4347682972> {"type": "and", "clauses": [{"field": "index", "value": 3, "type": "eq"}, {"field": "age", "lowerLimit": 20, "type": "range"}]}'

    >>> api.data.application('bucket_name').query_for_objects(clause)

    or

    >>> 'SQLAlchemy style'
    >>> api.data.application('bucket_name').query(clause).order_by('age').limit(3).all()
    >>> api.data.application('bucket_name').query(EqualClause('_id', 'abcd-efgh')).one()


Please refer source code and test code, for more information.


License
=========================

This software is released under the MIT License, see LICENSE.txt.
