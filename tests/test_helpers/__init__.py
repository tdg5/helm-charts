import json
from dataclasses import dataclass, field
from os import path
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

import pytest
import yaml
from pytest_helm_templates import HelmRunner

from tests.test_helpers.helper_renderer import HelperRenderer


@dataclass
class ChartDependency:
    name: str
    repository: str
    alias: Optional[str] = None
    condition: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    version: Optional[str] = None


ChartDependencies = Dict[str, ChartDependency]


def charts_path() -> str:
    test_helpers_path = Path(__file__).parent.parent
    _charts_path = test_helpers_path.joinpath("../charts")
    return path.normpath(str(_charts_path.absolute()))


def chart_path(
    chart_name: str,
    charts_path_override: Optional[str] = None,
) -> str:
    _charts_path = charts_path_override or charts_path()
    return f"{_charts_path}/{chart_name}"


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


def get_chart_yaml(
    chart_name: str,
    charts_path_override: Optional[str] = None,
) -> Dict:
    _chart_path = chart_path(chart_name, charts_path_override)
    chart_yaml_path = f"{_chart_path}/Chart.yaml"
    with open(chart_yaml_path, encoding="utf-8", mode="r") as file:
        chart_yaml = yaml.safe_load(file)
    assert isinstance(chart_yaml, Dict)
    return chart_yaml


def get_chart_values(
    chart_name: str,
    charts_path_override: Optional[str] = None,
) -> Dict:
    _chart_path = chart_path(chart_name, charts_path_override)
    chart_values_path = f"{_chart_path}/values.yaml"
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


def make_chart_fixtures(
    chart_dir_name: str,
    conftest_globals: Dict,
    charts_path_override: Optional[str] = None,
) -> None:
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
    def chart_yaml() -> Dict:
        return get_chart_yaml(chart_dir_name, charts_path_override)

    conftest_globals["chart_yaml"] = chart_yaml

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
    def helper_renderer(chart_name: str, helm_runner: HelmRunner) -> HelperRenderer:
        return HelperRenderer(
            chart_name=chart_name,
            helm_runner=helm_runner,
        )

    conftest_globals["helper_renderer"] = helper_renderer


def make_helm_runner(
    charts_path_override: Optional[str] = None,
) -> HelmRunner:
    _charts_path = charts_path_override or charts_path()
    return HelmRunner(cwd=_charts_path)


def random_string() -> str:
    return str(uuid4())
