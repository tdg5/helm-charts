from typing import Any, Dict

# A small map with a deliberate mix of value types (and a key containing a "/", as
# real annotation keys often do). Used to assert that templates pass annotations and
# labels through verbatim without coercing or dropping values.
EXAMPLE_MAPPING: Dict[str, Any] = {
    "one": 1,
    "two": "two",
    "three": 3.0,
    "four": True,
    "five/six": "true",
}

# A fixed Helm release name so name/label assertions are deterministic.
EXAMPLE_RELEASE_NAME = "release-name"
