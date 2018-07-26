import inspect
from typing import Dict, List
from collections import ChainMap
import uuid as u
import datetime


def filter_in(old_dict: Dict, keys: List[str]):
    return {key: old_dict[key] for key in keys if key in old_dict.keys()}


def get_args(a_dict, a_callable):
    init_params = function_params(a_callable)
    init_args = filter_in(a_dict, init_params)
    return init_args


def function_params(func):
    return list(inspect.signature(func).parameters.keys())


def call(func, kwargs):
    actual_args = get_args(kwargs, func)
    return func(**actual_args)


def dicts(*l):
    rev = list(reversed(l))
    return dict(ChainMap(*rev))


def uuid() -> str:
    return str(u.uuid4())


def utc_now():
    return datetime.datetime.utcnow()


def utc_now_str() -> str:
    return utc_now().isoformat()


def parse_isoformat_str(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")


def optional(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


if __name__ == '__main__':
    print(utc_now().isoformat())
