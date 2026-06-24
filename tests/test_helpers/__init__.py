import json
from dataclasses import dataclass, field
from os import path
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pytest
import yaml
from pytest_helm_templates import HelmRunner


@dataclass
class ChartDependency:
    name: str
    repository: str
    alias: Optional[str] = None
    condition: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    version: Optional[str] = None


ChartDependencies = Dict[str, ChartDependency]


class HelperRenderer:
    """
    Render a single named Helm template (a `define` block) in isolation so that
    helper logic can be unit-tested without rendering a full manifest.
    """

    def __init__(
        self,
        chart_name: str,
        helm_runner: HelmRunner,
        random_required_values: Dict[str, Any],
    ) -> None:
        self._chart_name = chart_name
        self._helm_runner = helm_runner
        self._random_required_values = random_required_values

    def render(
        self,
        helper_name: str,
        name: str = "",
        helper_namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
    ) -> str:
        namespace = helper_namespace or self._chart_name
        fully_qualified_name = f"{namespace}.{helper_name}"
        content = (
            "---\n"
            "result: |-\n"
            f'  {{{{- include "{fully_qualified_name}" . | nindent 2}}}}'
        )
        rendered = self._helm_runner.adhoc_template(
            chart=self._chart_name,
            content=content,
            name=name or random_string(),
            values=[self._random_required_values | (values or {})],
        )
        result = rendered["result"]
        assert isinstance(result, str)
        return result


def charts_path() -> str:
    tests_path = Path(__file__).parent.parent
    _charts_path = tests_path.joinpath("../charts")
    return path.normpath(str(_charts_path.absolute()))


def chart_path(
    chart_name: str,
    charts_path_override: Optional[str] = None,
) -> str:
    return f"{charts_path_override or charts_path()}/{chart_name}"


def make_helm_runner(charts_path_override: Optional[str] = None) -> HelmRunner:
    return HelmRunner(cwd=charts_path_override or charts_path())


def get_chart_yaml(
    chart_name: str,
    charts_path_override: Optional[str] = None,
) -> Dict:
    chart_yaml_path = f"{chart_path(chart_name, charts_path_override)}/Chart.yaml"
    with open(chart_yaml_path, encoding="utf-8", mode="r") as file:
        chart_yaml = yaml.safe_load(file)
    assert isinstance(chart_yaml, Dict)
    return chart_yaml


def get_chart_values(
    chart_name: str,
    charts_path_override: Optional[str] = None,
) -> Dict:
    chart_values_path = f"{chart_path(chart_name, charts_path_override)}/values.yaml"
    with open(chart_values_path, encoding="utf-8", mode="r") as file:
        chart_values = yaml.safe_load(file)
    assert isinstance(chart_values, Dict)
    return chart_values


def get_chart_values_schema(
    chart_name: str,
    charts_path_override: Optional[str] = None,
) -> Dict:
    _chart_path = chart_path(chart_name, charts_path_override)
    chart_values_schema_path = f"{_chart_path}/values.schema.json"
    with open(chart_values_schema_path, encoding="utf-8", mode="r") as file:
        chart_values_schema = json.loads(file.read())
    assert isinstance(chart_values_schema, Dict)
    return chart_values_schema


def get_chart_dependencies(chart_yaml: Dict) -> ChartDependencies:
    if "dependencies" not in chart_yaml:
        return {}

    return {
        dependency["name"]: ChartDependency(
            alias=dependency.get("alias"),
            condition=dependency.get("condition"),
            name=dependency["name"],
            repository=dependency["repository"],
            tags=dependency.get("tags", []),
            version=dependency.get("version"),
        )
        for dependency in chart_yaml["dependencies"]
    }


def make_chart_fixtures(
    chart_dir_name: str,
    conftest_globals: Dict,
    charts_path_override: Optional[str] = None,
) -> None:
    """
    Define a standard set of package-scoped pytest fixtures for a chart and inject
    them into the calling conftest's globals(), so each chart's conftest.py is a
    short call rather than a pile of boilerplate.
    """

    @pytest.fixture(scope="package")
    def chart_yaml() -> Dict:
        return get_chart_yaml(chart_dir_name, charts_path_override)

    conftest_globals["chart_yaml"] = chart_yaml

    @pytest.fixture(scope="package")
    def chart_name(chart_yaml: Dict) -> str:
        _chart_name = chart_yaml["name"]
        assert isinstance(_chart_name, str)
        return _chart_name

    conftest_globals["chart_name"] = chart_name

    @pytest.fixture(scope="package")
    def chart_version(chart_yaml: Dict) -> str:
        _chart_version = chart_yaml["version"]
        assert isinstance(_chart_version, str)
        return _chart_version

    conftest_globals["chart_version"] = chart_version

    @pytest.fixture(scope="package")
    def app_version(chart_yaml: Dict) -> str:
        _app_version = chart_yaml["appVersion"]
        assert isinstance(_app_version, str)
        return _app_version

    conftest_globals["app_version"] = app_version

    @pytest.fixture(scope="package")
    def chart_dependencies(chart_yaml: Dict) -> ChartDependencies:
        return get_chart_dependencies(chart_yaml)

    conftest_globals["chart_dependencies"] = chart_dependencies

    @pytest.fixture(scope="package")
    def chart_values() -> Dict:
        return get_chart_values(chart_dir_name, charts_path_override)

    conftest_globals["chart_values"] = chart_values

    @pytest.fixture(scope="package")
    def chart_values_schema() -> Dict:
        return get_chart_values_schema(chart_dir_name, charts_path_override)

    conftest_globals["chart_values_schema"] = chart_values_schema

    @pytest.fixture(scope="package")
    def chart_computed_values(chart_name: str, helm_runner: HelmRunner) -> Dict:
        return helm_runner.computed_values(chart=chart_name)

    conftest_globals["chart_computed_values"] = chart_computed_values

    @pytest.fixture(scope="package")
    def helper_renderer(
        chart_name: str,
        helm_runner: HelmRunner,
        random_required_values: Dict[str, Any],
    ) -> HelperRenderer:
        return HelperRenderer(
            chart_name=chart_name,
            helm_runner=helm_runner,
            random_required_values=random_required_values,
        )

    conftest_globals["helper_renderer"] = helper_renderer

    @pytest.fixture(scope="package")
    def random_required_values() -> Dict[str, Any]:
        """
        A dictionary of all values a chart requires, with random values that can't be
        relied upon for testing.

        Expected to be overridden by any package that tests a chart with required
        values.
        """
        return {}

    conftest_globals["random_required_values"] = random_required_values


def random_string() -> str:
    return str(uuid4())
