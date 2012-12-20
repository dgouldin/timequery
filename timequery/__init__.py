from datetime import datetime
from types import MethodType

from dateutil.relativedelta import relativedelta

class Query(object):
    # transform units
    YEAR = 'year'
    MONTH = 'month'
    WEEK = 'week'
    DAY = 'day'
    HOUR = 'hour'
    MINUTE = 'minute'

    # transform types
    BEGINNING_OF = 'beginning_of'
    NEXT = 'next'
    LAST = 'last'

    # aliases
    ALIASES = {
        'midnight': (BEGINNING_OF, DAY),
        'yesterday': (LAST, DAY),
        'tomorrow': (NEXT, DAY),
    }

    TRANSFORM_KWARGS = {
        BEGINNING_OF: {
            YEAR: {'month': 1, 'day': 1},
            MONTH: {'day': 1},
            WEEK: {'weekday': 0, 'weeks': -1},
            DAY: {'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0},
            HOUR: {'minute': 0, 'second': 0, 'microsecond': 0},
            MINUTE: {'second': 0, 'microsecond': 0},
        },
        NEXT: {
            YEAR: {'years': 1},
            MONTH: {'months': 1},
            WEEK: {'weeks': 1},
            DAY: {'days': 1},
            HOUR: {'hours': 1},
            MINUTE: {'minutes': 1},
        },
        LAST: {
            YEAR: {'years': -1},
            MONTH: {'months': -1},
            WEEK: {'weeks': -1},
            DAY: {'days': -1},
            HOUR: {'hours': -1},
            MINUTE: {'minutes': -1},
        },
    }

    def __init__(self, as_of=None):
        self.as_of = as_of
        self.transforms = []
        self.transformed = None

    def _add_transform(self, transform_type, transform_unit):

        kwargs = self.TRANSFORM_KWARGS.get(transform_type)
        if not kwargs:
            raise ValueError('Unknown transform type: %s' % transform_type)
        kwargs = kwargs.get(transform_unit)
        if not kwargs:
            raise ValueError('Unknown transform unit: %s' % trasnform_unit)
        clone = self._clone()
        clone.transforms.append((transform_type, transform_unit))
        return clone

    def _clone(self):
        clone = Query(as_of=self.as_of)
        clone.transforms = self.transforms[:]
        return clone

    def _transform(self):
        if not self.transformed:
            transformed = self.as_of or datetime.now()
            for ttype, tunit in self.transforms:
                transformed += relativedelta(
                    **self.TRANSFORM_KWARGS[ttype][tunit])
            self.transformed = transformed
        return self.transformed

    def datetime(self):
        return self._transform()

    def date(self):
        return self.datetime().date()

    def time(self):
        return self.datetime().time()

# contribute transform shortcut functions
def _transform_func(transform_type, transform_unit, name):
    def func(self):
        return self._add_transform(transform_type, transform_unit)
    func.__name__ = '_'.join((transform_type, transform_unit))
    return func

for ttype, tunit_kwargs in Query.TRANSFORM_KWARGS.items():
    for tunit, kwargs in tunit_kwargs.items():
        name = '_'.join((ttype, tunit))
        func = _transform_func(ttype, tunit, name)
        setattr(Query, name, MethodType(func, None, Query))

# contribute alias functions
def _alias_func(transform_type, transform_unit, name):
    def func(self, *args, **kwargs):
        return getattr(self, '_'.join((transform_type, transform_unit)))(
            *args, **kwargs)
    func.__name__ = alias
    return func

for alias, (ttype, tunit) in Query.ALIASES.items():
    func = _alias_func(ttype, tunit, alias)
    setattr(Query, alias, MethodType(func, None, Query))

