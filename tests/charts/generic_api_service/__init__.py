from typing import Any, Dict

from tests.test_helpers import random_string

CHART_NAME = "generic-api-service"
EXAMPLE_APP_NAME = "app-name"
EXAMPLE_APP_VERSION = "app-version"


def random_required_values() -> Dict[str, Any]:
    """
    Return a dictionary that includes all required values, but with values that
    are random and can't be relied upon for testing.
    """
    return {
        "appName": random_string(),
        "container": {
            "image": {
                "repository": random_string(),
                "tag": random_string(),
            },
        },
    }
