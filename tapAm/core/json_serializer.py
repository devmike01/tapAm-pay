from rest_framework.utils import json
from django.core import serializers


def extract_fields(data) -> dict:
    list_json = json.loads(serializers.serialize('json',
                                                 [data, ]))
    return list_json[0]['fields']


def extract_error(err):
    print(type(err))
    try:
        error_dict = dict(err.__dict__.get('detail'))
        detail = list(error_dict.values())[-1]
        field = list(error_dict.keys())[-1]
        return f"{field}: {detail[0].title()}".lower()
    except Exception:
        return 'Bad request. Check your request and try again.'


def _db_to_json(db_data):
    return serializers.serialize('json', [db_data, ])
