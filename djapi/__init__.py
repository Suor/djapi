"""
Principles:
- library not framework (helpers + decorators)
- avoid abstractions, especially IOC
- simplicity of implementation matters
- reuse django (i.e. validation)
    - when impossible to reuse, mimic it
- do not hide intentions
    - the less abstraction the better (.json() instead of .response())

DWIM, practicality
"""

import six
import cgi
import json as _json
from funcy import decorator, chain, select_values
from funcy import cached_property, rcompose, memoize, iffy, isa, partial, walk_values, flip

import django
from django import forms
from django.core.exceptions import FieldError, ValidationError
from django.urls import reverse_lazy
from django.db.models import F
from django.http import HttpResponseNotAllowed
from django.shortcuts import _get_queryset, render

from .auth import auth_required, user_passes_test  # noqa
from .response import json


# Querysets
# TODO: review this in Django 1.9+, there is no built-in QuerySet sublclasses
@memoize  # noqa
def _extend_queryset_class(base):
    class _QuerySet(base):
        @cached_property
        def _mappers(self):
            return []

        def _clone(self, **kwargs):
            clone = base._clone(self, **kwargs)
            clone._mappers = self._mappers
            return clone

        def _fetch_all(self):
            it = self._iterable_class(self)
            self._result_cache = map(rcompose(*self._mappers), it)

            # Fill in the rest
            base._fetch_all(self)

        def map(self, func):
            clone = self._clone()
            clone._mappers.append(func)
            return clone

        def map_types(self, types, func):
            return self.map(partial(walk_values, iffy(isa(types), func)))

        def values(self, *fields, **expressions):
            """
            Extended version supporting renames:
                .values('id', 'name', author__name='author')
            """
            renames = select_values(isa(six.string_types), expressions)
            if not renames:
                return base.values(self, *fields, **expressions)
            elif django.VERSION >= (1, 11):
                rename_expressions = walk_values(F, renames)
                expressions.update(rename_expressions)
                return base.values(self, *fields, **expressions)
            else:
                f_to_name = flip(renames)
                rename = lambda d: {f_to_name.get(k, k): v for k, v in d.items()}
                return base.values(self, *chain(fields, f_to_name)).map(rename)

        # TODO: .values_list_but() ?
        def values_but(self, *exclude):
            exclude = set(exclude)
            attnames = {f.name: f.attname for f in self.model._meta.fields}
            known = set(attnames) | set(attnames.values()) | {'pk'}
            unknown = exclude - known
            if unknown:
                raise FieldError("Cannot resolve keyword%(p)s %(unknown)s into field%(p)s. "
                                 "Choices are: %(known)s." % {
                                     'unknown': ', '.join(sorted(unknown)),
                                     'known': ', '.join(sorted(known)),
                                     'p': 's' if len(unknown) > 1 else '',
                                 })

            fields = [att for name, att in attnames.items() if not {name, att} & exclude]
            return self.values(*fields)

        def values_add(self, *fields, **expressions):
            return self.values(*(self._fields + fields), **expressions)

    _QuerySet.__name__ = 'API' + base.__name__
    return _QuerySet

def queryset(qs):
    qs = _get_queryset(qs)
    qs.__class__ = _extend_queryset_class(qs.__class__)
    return qs

def get_or_404(qs, *args, **kwargs):
    qs = _get_queryset(qs)
    try:
        return qs.get(*args, **kwargs)
    except qs.model.DoesNotExist as e:
        return json(404, detail=e.args[0])


@decorator
def catch(call, exception, status=500, message=None):
    try:
        return call()
    except exception as e:
        return json(status, detail=message or str(e))

def paginate(request, qs, per_page=None):
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', per_page)
    # TODO: better error message
    if limit is None:
        return json(400, detail='limit parameter is required')
    try:
        offset = int(offset)
        limit = int(limit)
    except ValueError:
        return json(400, detail='Bad value for offset or limit parameter')

    count = qs.count()
    if offset >= count:
        return json(404, detail='offset is too big', count=count)
    page = qs[offset:offset + limit]

    uri = _request_uri(request)
    if limit == per_page:
        uri_template = uri + '?offset=%d'
    else:
        uri_template = uri + '?limit=%d&offset=%%d' % limit
    return {
        'count': count,
        'next': uri_template % (offset + limit) if offset + limit < count else None,
        'previous': uri_template % (offset - limit) if offset > limit else None,
        'results': page,
    }

def _request_uri(request):
    return '{scheme}://{host}{path}'.format(
        scheme=request.scheme, host=request.get_host(), path=request.path)


# Forms

class JSONField(forms.Field):
    def to_python(self, value):
        if value is None or isinstance(value, (dict, list)):
            return value
        try:
            return _json.loads(value)
        except ValueError as e:
            raise ValidationError(unicode(e))


def show_form(form, action=None, view=None):
    assert (action is None) != (view is None), "Specify action or view, but not both"
    if action is None:
        action = reverse_lazy(view)
    return lambda request: render(request, 'test_form.j2', {'form': form(), 'action': action})


@decorator
def validate(call, form=None):
    # request.content_type is new in Django 1.10
    if hasattr(call.request, 'content_type'):
        content_type = call.request.content_type
    else:
        content_type, _ = cgi.parse_header(call.request.META.get('CONTENT_TYPE', ''))
    # Parse JSON or fallback to urlencoded
    if content_type == 'application/json':
        try:
            data = _json.loads(call.request.body)
        except ValueError:
            return json(400, detail="Failed parsing JSON")
    else:
        data = call.request.POST

    aform = form(data)
    if not aform.is_valid():
        return json(400, detail='Validation failed', errors=aform._errors)

    return call(aform.save(commit=False) if hasattr(aform, 'save') else aform.cleaned_data)


# Routing

def route(**methods):
    permitted = sorted(m.upper() for m in methods)

    def routed(request, *args, **kwargs):
        method = request.method.lower()
        if method not in methods:
            return HttpResponseNotAllowed(permitted)
        return methods[method](request, *args, **kwargs)

    routed.csrf_exempt = True
    return routed


def get_post(get, post):
    return route(get=get, post=post)
