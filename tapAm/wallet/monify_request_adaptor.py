import json


def monify_create_wallet(data: dict):
    return json.dumps(monify_re_write_data(data))


def monify_re_write_data(data: dict):
    """Recursively convert all dict keys to camelCase."""
    result = {}
    for key, value in data.items():
        new_key = to_camel_case(key)

        if isinstance(value, dict):
            result[new_key] = monify_re_write_data(value)
        elif isinstance(value, list):
            # Handle lists of dicts
            result[new_key] = [
                monify_re_write_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[new_key] = value
    return result


def to_camel_case(value, i=0):
    if not value or not (isinstance(value, str) and i < len(value)):
        return '-'
    if i == len(value) - 1:
        return '' if value[i] == '_' else value[i]
    underscore = False
    j = i
    while j < len(value) and value[j] == '_':
        j += 1
        underscore = True

    if len(value) == j:
        return ''

    return (value[j].upper() if underscore else value[j]) + to_camel_case(value, j + 1)


# _bala_ce_

def adapt_create_wallet(data: dict):
    if isinstance(data, dict):
        new_case = monify_create_wallet(data)
        adapt_create_wallet(data)
    elif isinstance(data, list):
        return [to_camel_case(v) for v in data]
    return data


print(monify_create_wallet({
    "wallet_reference": "ref16842048425966",
    "wallet_name": "Staging Wallet - ref16804248425966",
    "customer_name": "Gbenga Dev",
    "bvn_details": {
        "bvn": "22203056828",
        "bvn_date_of_birth": "1995-05-07"
    },
    "customer_email": "dev.gbenga@gmail.com"
}))
