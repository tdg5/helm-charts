from typing import Dict, List, Optional, cast

import yaml
from pytest_helm_templates import HelmRunner

from tests.charts.generic_api_service import (
    CHART_NAME,
    EXAMPLE_APP_NAME,
    EXAMPLE_APP_VERSION,
    random_required_values,
)
from tests.test_helpers import HelperRenderer, random_string
from tests.test_helpers.test_constants import EXAMPLE_MAPPING, EXAMPLE_RELEASE_NAME


def test_http_route_resource_is_omitted_by_default(helm_runner: HelmRunner) -> None:
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[random_required_values()],
    )
    assert len(resources) > 0
    assert all([resource.get("kind") != "HTTPRoute" for resource in resources])


def test_resource_is_omitted_when_create_is_false(helm_runner: HelmRunner) -> None:
    values = random_required_values() | {
        "httpRoutes": {
            "identifier": {
                "create": False,
                "parentRefs": {"gateway": {"name": "gateway-name"}},
                "rules": {
                    "rule": {"backendRefs": {"http": {"portName": "http"}}},
                },
            },
        },
    }
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[values],
    )
    assert len(resources) > 0
    assert all([resource.get("kind") != "HTTPRoute" for resource in resources])


def test_static_values_and_defaults(
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    values = {
        "appName": EXAMPLE_APP_NAME,
        "appVersion": EXAMPLE_APP_VERSION,
    }
    subject = render_subjects(
        helm_runner=helm_runner, name=release_name, values=values
    )[0]

    assert subject["kind"] == "HTTPRoute"

    default_api_version = helper_renderer.render(
        helper_name="http-route-api-version",
        name=release_name,
        values=values,
    )

    assert subject["apiVersion"] == default_api_version

    default_full_name = helper_renderer.render(
        "full-name",
        name=release_name,
        values=values,
    )

    default_labels_yaml = helper_renderer.render(
        "labels",
        name=release_name,
        values=values,
    )
    default_labels = yaml.safe_load(default_labels_yaml)

    metadata = subject["metadata"]
    assert metadata["labels"] == default_labels
    assert metadata["name"] == default_full_name
    assert "namespace" not in metadata
    assert "annotations" not in metadata


def test_api_version_defaults_to_gateway_v1(helm_runner: HelmRunner) -> None:
    subject = render_subjects(helm_runner=helm_runner)[0]
    assert subject["apiVersion"] == "gateway.networking.k8s.io/v1"


def test_api_version_can_be_set_with_global_gateway_api_value(
    helm_runner: HelmRunner,
) -> None:
    api_version = "gateway.networking.k8s.io/v1beta1"
    subject = render_subjects(
        helm_runner=helm_runner,
        values={"global": {"gatewayApi": {"apiVersion": api_version}}},
    )[0]
    assert subject["apiVersion"] == api_version


def test_name_can_be_overridden_with_the_name_value(helm_runner: HelmRunner) -> None:
    name = random_string()
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "httpRoutes": {
                "identifier": {"name": name},
            },
        },
    )[0]
    assert subject["kind"] == "HTTPRoute"
    assert subject["metadata"]["name"] == name


def test_annotations_can_be_configured_with_the_annotations_value(
    helm_runner: HelmRunner,
) -> None:
    annotations = EXAMPLE_MAPPING
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "httpRoutes": {
                "identifier": {"annotations": annotations},
            },
        },
    )[0]
    assert subject["kind"] == "HTTPRoute"
    assert subject["metadata"]["annotations"] == annotations


def test_parent_refs_can_be_configured_with_the_parent_refs_value(
    helm_runner: HelmRunner,
) -> None:
    parent_refs = {
        "gateway-1": {
            "name": "gateway-1-name",
            "namespace": "gateway-1-namespace",
            "sectionName": "gateway-1-section",
            "port": 8443,
        },
        "gateway-2": {
            "name": "gateway-2-name",
        },
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "httpRoutes": {
                "identifier": {"parentRefs": parent_refs},
            },
        },
    )[0]
    assert subject["kind"] == "HTTPRoute"

    rendered_parent_refs = subject["spec"]["parentRefs"]
    assert len(rendered_parent_refs) == len(parent_refs)

    rendered_by_name = {ref["name"]: ref for ref in rendered_parent_refs}

    full = rendered_by_name["gateway-1-name"]
    assert full["namespace"] == "gateway-1-namespace"
    assert full["sectionName"] == "gateway-1-section"
    assert full["port"] == 8443

    minimal = rendered_by_name["gateway-2-name"]
    assert minimal == {"name": "gateway-2-name"}


def test_hostnames_can_be_configured_with_the_hostnames_value(
    helm_runner: HelmRunner,
) -> None:
    hostnames = {
        "example_dot_com": "example.com",
        "other_dot_example_dot_com": "other.example.com",
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "httpRoutes": {
                "identifier": {"hostnames": hostnames},
            },
        },
    )[0]
    assert subject["kind"] == "HTTPRoute"
    assert sorted(subject["spec"]["hostnames"]) == sorted(hostnames.values())


def test_hostnames_can_be_omitted(helm_runner: HelmRunner) -> None:
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "httpRoutes": {
                "identifier": {"hostnames": None},
            },
        },
    )[0]
    assert subject["kind"] == "HTTPRoute"
    assert "hostnames" not in subject["spec"]


def test_rules_and_backend_refs_can_be_configured(
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    service_name = random_string()
    other_service_name = random_string()
    rules = {
        "rule-id-1": {
            "backendRefs": {
                "backend-default-service": {"portName": "http"},
                "backend-explicit-service": {
                    "name": other_service_name,
                    "portName": "https",
                    "weight": 7,
                },
            },
        },
    }
    values = {
        "httpRoutes": {
            "identifier": {"rules": rules},
        },
        "ports": {
            "http": {
                "containerPort": 8080,
                "name": "http",
                "protocol": "TCP",
                "servicePort": 80,
            },
            "https": {
                "containerPort": 8443,
                "name": "https",
                "protocol": "TCP",
                "servicePort": 443,
            },
        },
        "service": {"name": service_name},
    }
    subject = render_subjects(helm_runner=helm_runner, values=values)[0]
    assert subject["kind"] == "HTTPRoute"

    expected_service_name = helper_renderer.render(
        "service-name",
        values={"service": {"name": service_name}},
    )

    rendered_rules = subject["spec"]["rules"]
    assert len(rendered_rules) == 1

    backend_refs = rendered_rules[0]["backendRefs"]
    backend_refs_by_name = {ref["name"]: ref for ref in backend_refs}

    default_backend = backend_refs_by_name[expected_service_name]
    assert default_backend["port"] == 80
    assert "weight" not in default_backend

    explicit_backend = backend_refs_by_name[other_service_name]
    assert explicit_backend["port"] == 443
    assert explicit_backend["weight"] == 7


def test_backend_ref_weight_of_zero_is_preserved(
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    # weight: 0 has explicit drain-traffic semantics in the Gateway API spec and
    # is distinct from omitting weight (which defaults to 1), so it must not be
    # dropped as a falsey value.
    service_name = random_string()
    values = {
        "httpRoutes": {
            "identifier": {
                "rules": {
                    "rule-id-1": {
                        "backendRefs": {
                            "drained-backend": {"portName": "http", "weight": 0},
                        },
                    },
                },
            },
        },
        "ports": {
            "http": {
                "containerPort": 8080,
                "name": "http",
                "protocol": "TCP",
                "servicePort": 80,
            },
        },
        "service": {"name": service_name},
    }
    subject = render_subjects(helm_runner=helm_runner, values=values)[0]

    expected_service_name = helper_renderer.render(
        "service-name",
        values={"service": {"name": service_name}},
    )

    backend_refs = subject["spec"]["rules"][0]["backendRefs"]
    backend_refs_by_name = {ref["name"]: ref for ref in backend_refs}

    drained_backend = backend_refs_by_name[expected_service_name]
    assert drained_backend["weight"] == 0


def test_matches_can_be_configured(helm_runner: HelmRunner) -> None:
    matches = {
        "root": {
            "path": {"type": "PathPrefix", "value": "/"},
            "method": "GET",
        },
        "exact": {
            "path": {"type": "Exact", "value": "/health"},
        },
    }
    rules = {
        "rule-id-1": {
            "backendRefs": {"http": {"portName": "http"}},
            "matches": matches,
        },
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "httpRoutes": {
                "identifier": {"rules": rules},
            },
        },
    )[0]
    assert subject["kind"] == "HTTPRoute"

    rendered_matches = subject["spec"]["rules"][0]["matches"]
    assert len(rendered_matches) == len(matches)

    matches_by_value = {match["path"]["value"]: match for match in rendered_matches}

    root = matches_by_value["/"]
    assert root["path"]["type"] == "PathPrefix"
    assert root["method"] == "GET"

    exact = matches_by_value["/health"]
    assert exact["path"]["type"] == "Exact"
    assert "method" not in exact


def test_matches_can_be_omitted(helm_runner: HelmRunner) -> None:
    rules = {
        "rule-id-1": {
            "backendRefs": {"http": {"portName": "http"}},
        },
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "httpRoutes": {
                "identifier": {"rules": rules},
            },
        },
    )[0]
    assert subject["kind"] == "HTTPRoute"
    assert "matches" not in subject["spec"]["rules"][0]


def render_subjects(
    helm_runner: HelmRunner,
    name: Optional[str] = None,
    values: Optional[Dict] = None,
) -> List[Dict]:
    _name = name or random_string()
    _values = random_required_values() | (values or {})

    default_http_route_values = {
        "create": True,
        "parentRefs": {
            random_string(): {"name": random_string()},
        },
        "rules": {
            random_string(): {
                "backendRefs": {
                    random_string(): {"portName": "http"},
                },
            },
        },
    }
    http_routes_values = cast(
        Dict[str, Dict], _values.get("httpRoutes") or {"identifier": {}}
    )
    _values["httpRoutes"] = {
        key: (default_http_route_values | http_route_values)
        for key, http_route_values in http_routes_values.items()
    }

    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/http_routes.yaml"],
        values=[_values],
    )
    return manifests
