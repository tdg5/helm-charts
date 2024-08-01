from typing import Any, Dict
from uuid import uuid4


def dict_with_keys_of_string_and_values_of_any() -> Dict[str, Any]:
    return {
        "one": "one",
        "two": 2.0,
        "three": 3,
        "four": False,
        "five/six": "true",
        "seven": random_string(),
    }


def random_string() -> str:
    return str(uuid4())
