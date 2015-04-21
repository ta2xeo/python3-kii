from copy import deepcopy
from enum import Enum, unique
import json

from kii import exceptions as exc


class Clause:
    def __str__(self):
        return '<Clause Object:{0}> {1}'.format(
            id(self),
            json.dumps(self.query(), ensure_ascii=False))

    @classmethod
    def all(cls):
        return AllClause()

    @classmethod
    def and_(cls, *clauses):
        return AndClause(*clauses)

    @classmethod
    def eq(cls, field, value):
        return EqualClause(field, value)

    @classmethod
    def in_(cls, field, values):
        return InClause(field, values)

    @classmethod
    def not_(cls, clause):
        return NotClause(clause)

    @classmethod
    def or_(cls, *clauses):
        return OrClause(*clauses)

    @classmethod
    def prefix(cls, field, prefix):
        return PrefixClause(field, prefix)

    def clone(self):
        return deepcopy(self)


class AllClause(Clause):
    def query(self):
        return {'type': 'all'}


class AndClause(Clause):
    def __init__(self, *clauses):
        for c in clauses:
            if not isinstance(c, Clause):
                raise exc.KiiInvalidClauseError

        self.children = list(clauses)

    def __len__(self):
        return len(self.children)

    def add(self, clause):
        if not isinstance(clause, Clause):
            raise exc.KiiInvalidClauseError

        self.children.append(clause)
        return self

    def query(self):
        return {
            'type': 'and',
            'clauses': [c.query() for c in self.children],
        }


class EqualClause(Clause):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def query(self):
        return {
            'type': 'eq',
            'field': self.field,
            'value': self.value,
        }


class GeoBoxClause(Clause):
    def __init__(self, field, ne_lat, ne_lon, sw_lat, sw_lon):
        self.field = field
        self.ne_lat = ne_lat
        self.ne_lon = ne_lon
        self.sw_lat = sw_lat
        self.sw_lon = sw_lon

    def query(self):
        return {
            'type': 'geobox',
            'field': self.field,
            'box': {
                'ne': {
                    '_type': 'point',
                    'lat': self.ne_lat,
                    'lon': self.ne_lon,
                },
                'sw': {
                    '_type': 'point',
                    'lat': self.sw_lat,
                    'lon': self.sw_lon,
                }
            }
        }


class GeoDistanceClause(Clause):
    def __init__(self, field, center_lat, center_lon, radius, put_distance_into=None):
        self.field = field
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius = radius
        self.put_distance_into = put_distance_into

    def query(self):
        params = {
            'type': 'geodistance',
            'field': self.field,
            'center': {
                '_type': 'point',
                'lat': self.center_lat,
                'lon': self.center_lon,
            },
            'radius': self.radius,
        }
        if self.put_distance_into is not None:
            params['putDistanceInto'] = self.put_distance_into

            return params


class HasFieldClause(Clause):
    @unique
    class Types(Enum):
        string = 'STRING'
        integer = 'INTEGER'
        decimal = 'DECIMAL'
        boolean = 'BOOLEAN'

    def __init__(self, field, field_type):
        self.field = field
        if not isinstance(field_type, HasFieldClause.Types):
            field_type = HasFieldClause.Types(field_type)
        self.field_type = field_type

    def query(self):
        return {
            'type': 'hasField',
            'field': self.field,
            'fieldType': self.field_type.value,
        }


class InClause(Clause):
    def __init__(self, field, values):
        self.field = field
        if not isinstance(values, (tuple, list)):
            values = tuple(values)
        self.values = values

    def query(self):
        return {
            'type': 'in',
            'field': self.field,
            'values': self.values,
        }


class NotClause(Clause):
    def __init__(self, clause):
        if not isinstance(clause, Clause):
            raise exc.KiiInvalidClauseError

        self.clause = clause

    def query(self):
        return {
            'type': 'not',
            'clause': self.clause.query(),
        }


class OrClause(AndClause):
    def query(self):
        return {
            'type': 'or',
            'clauses': [c.query() for c in self.children],
        }


class PrefixClause(Clause):
    def __init__(self, field, prefix):
        self.field = field
        self.prefix = prefix

    def query(self):
        return {
            'type': 'prefix',
            'field': self.field,
            'prefix': self.prefix,
        }


class RangeClause(Clause):
    def __init__(self, field):
        self.field = field
        self.lower_limit = None
        self.lower_included = True
        self.upper_limit = None
        self.upper_included = True

    def query(self):
        query = {
            'type': 'range',
            'field': self.field,
        }
        if self.lower_limit is not None:
            query['lowerLimit'] = self.lower_limit
            if not self.lower_included:
                query['lowerIncluded'] = self.lower_included

        if self.upper_limit is not None:
            query['upperLimit'] = self.upper_limit
            if not self.upper_included:
                query['upperIncluded'] = self.upper_included

        return query

    def ge(self, lower_limit):
        self.lower_limit = lower_limit
        self.lower_included = True
        return self

    def gt(self, lower_limit):
        self.lower_limit = lower_limit
        self.lower_included = False
        return self

    def le(self, upper_limit):
        self.upper_limit = upper_limit
        self.upper_included = True
        return self

    def lt(self, upper_limit):
        self.upper_limit = upper_limit
        self.upper_included = False
        return self
