from typing import Any, Dict

import pytest
from pytest_helm_templates import HelmRunner

from tests.charts.generic_api_service import CHART_NAME
from tests.charts.generic_api_service import (
    random_required_values as _random_required_values,
)
from tests.test_helpers import make_chart_fixtures, make_helm_runner


# Override the helm_runner fixture so it can also ensure chart dependencies are
# installed before any template is rendered.
@pytest.fixture(scope="package")
def helm_runner() -> HelmRunner:
    helm_runner = make_helm_runner()
    helm_runner.dependency_update_if_missing(chart=CHART_NAME)
    return helm_runner


make_chart_fixtures(
    chart_dir_name=CHART_NAME,
    conftest_globals=globals(),
)


@pytest.fixture(scope="package")
def random_required_values() -> Dict[str, Any]:
    return _random_required_values()
