from typing import Dict, Optional
from uuid import uuid4

import yaml
from pytest_helm_templates import HelmRunner

from tests.charts.generic_api_service import (
    CHART_NAME,
    EXAMPLE_APP_NAME,
    EXAMPLE_APP_VERSION,
    random_required_values,
)
from tests.test_helpers import HelperRenderer
from tests.test_helpers.test_constants import EXAMPLE_RELEASE_NAME


def test_static_values_and_defaults(
    chart_values: Dict,
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    values = {"appName": EXAMPLE_APP_NAME, "appVersion": EXAMPLE_APP_VERSION}
    subject = render_subject(
        helm_runner=helm_runner,
        name=release_name,
        values=values,
    )

    assert subject["apiVersion"] == "v1"
    assert subject["kind"] == "Service"

    metadata = subject["metadata"]

    default_labels_yaml = helper_renderer.render(
        "labels",
        name=release_name,
        values=values,
    )
    default_labels = yaml.safe_load(default_labels_yaml)
    assert metadata["labels"] == default_labels

    # Name is expected to be there, but it takes a random value for this test.
    assert "name" in metadata

    assert "namespace" not in metadata

    spec = subject["spec"]
    ports = spec["ports"]

    service_ports_by_name = {port["name"]: port for port in ports}
    default_ports_by_name = {
        port["name"]: {
            "name": port["name"],
            "port": port["servicePort"],
            "protocol": port["protocol"],
            "targetPort": port["name"],
        }
        for port in chart_values["ports"].values()
    }
    assert service_ports_by_name == default_ports_by_name

    default_selector_labels_yaml = helper_renderer.render(
        "selector-labels",
        name=release_name,
        values=values,
    )
    default_selector_labels = yaml.safe_load(default_selector_labels_yaml)
    assert spec["selector"] == default_selector_labels

    assert spec["type"] == chart_values["service"]["type"]


def test_service_resource_can_be_omitted(helm_runner: HelmRunner) -> None:
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[random_required_values() | {"service": {"create": False}}],
    )
    assert len(resources) > 0
    assert all(resource.get("kind") != "Service" for resource in resources)


def test_ports_can_be_customized_with_ports_value(
    helm_runner: HelmRunner,
) -> None:
    new_port = {
        "containerPort": 2379,
        "name": "new",
        "protocol": "TCP",
        "servicePort": 2379,
    }
    ports = {
        "new": new_port,
        "http": None,
    }
    subject = render_subject(
        helm_runner=helm_runner,
        values={"ports": ports},
    )

    service_ports_by_name = {port["name"]: port for port in subject["spec"]["ports"]}
    assert "http" not in service_ports_by_name

    service_new_port = service_ports_by_name["new"]
    assert service_new_port["name"] == new_port["name"]
    assert service_new_port["port"] == new_port["servicePort"]
    assert service_new_port["protocol"] == new_port["protocol"]
    assert service_new_port["targetPort"] == new_port["name"]
    assert "containerPort" not in service_new_port
    assert "servicePort" not in service_new_port


def test_name_can_be_customized_with_service_name_value(
    helm_runner: HelmRunner,
) -> None:
    service_name = "service-name"
    subject = render_subject(
        helm_runner=helm_runner,
        values={"service": {"name": service_name}},
    )

    assert subject["metadata"]["name"] == service_name


def test_type_can_be_customized_with_service_type_value(
    helm_runner: HelmRunner,
) -> None:
    service_type = "NodePort"
    subject = render_subject(
        helm_runner=helm_runner,
        values={"service": {"name": str(uuid4()), "type": service_type}},
    )

    assert subject["spec"]["type"] == service_type


def render_subject(
    helm_runner: HelmRunner,
    name: Optional[str] = None,
    values: Dict = {},
) -> Dict:
    _name = name or str(uuid4())
    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/service.yaml"],
        values=[random_required_values() | values],
    )
    subject = manifests[0]
    assert subject["kind"] == "Service"
    return subject
