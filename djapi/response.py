import json as _json
from funcy import is_iter

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import QuerySet
from django.http import HttpResponse


class SmarterJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, QuerySet) or is_iter(o):
            return list(o)
        else:
            return super(SmarterJSONEncoder, self).default(o)

def json(*args, **kwargs):
    if len(args) > 1 and kwargs:
        raise TypeError("json() accepts data either via positional argument or keyword, not both")
    if not 1 <= len(args) <= 2:
        raise TypeError("json() takes from 1 to 2 positional arguments but %d were given"
                        % len(args))
    if kwargs:
        status = args[0] if args else 200
        data = kwargs
    elif len(args) == 1:
        status, data = 200, args[0]
    else:
        status, data = args

    if not isinstance(status, int):
        raise TypeError("HTTP status should be int not %s" % status)

    # Allow response pass through, e.g. error
    if isinstance(data, HttpResponse):
        return data
    # Pretty print in debug mode
    if settings.DEBUG:
        json_data = _json.dumps(data, cls=SmarterJSONEncoder, indent=4)
    else:
        json_data = _json.dumps(data, cls=SmarterJSONEncoder, separators=(',', ':'))
    return HttpResponse(json_data, status=status, content_type='application/json')
