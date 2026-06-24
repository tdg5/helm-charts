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


def test_backend_tls_policy_resource_is_omitted_by_default(
    helm_runner: HelmRunner,
) -> None:
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[random_required_values()],
    )
    assert len(resources) > 0
    assert all([resource.get("kind") != "BackendTLSPolicy" for resource in resources])


def test_resource_is_omitted_when_create_is_false(helm_runner: HelmRunner) -> None:
    values = random_required_values() | {
        "backendTLSPolicies": {
            "identifier": {
                "create": False,
                "targetRefs": {"service": {}},
                "validation": {
                    "wellKnownCACertificates": "System",
                    "hostname": "example.com",
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
    assert all([resource.get("kind") != "BackendTLSPolicy" for resource in resources])


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

    assert subject["kind"] == "BackendTLSPolicy"

    default_api_version = helper_renderer.render(
        helper_name="backend-tls-policy-api-version",
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


def test_api_version_defaults_to_gateway_v1alpha3(helm_runner: HelmRunner) -> None:
    subject = render_subjects(helm_runner=helm_runner)[0]
    assert subject["apiVersion"] == "gateway.networking.k8s.io/v1alpha3"


def test_api_version_can_be_set_with_global_gateway_api_value(
    helm_runner: HelmRunner,
) -> None:
    api_version = "gateway.networking.k8s.io/v1"
    subject = render_subjects(
        helm_runner=helm_runner,
        values={"global": {"gatewayApi": {"backendTlsPolicyApiVersion": api_version}}},
    )[0]
    assert subject["apiVersion"] == api_version


def test_name_can_be_overridden_with_the_name_value(helm_runner: HelmRunner) -> None:
    name = random_string()
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTLSPolicies": {
                "identifier": {"name": name},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTLSPolicy"
    assert subject["metadata"]["name"] == name


def test_annotations_can_be_configured_with_the_annotations_value(
    helm_runner: HelmRunner,
) -> None:
    annotations = EXAMPLE_MAPPING
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTLSPolicies": {
                "identifier": {"annotations": annotations},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTLSPolicy"
    assert subject["metadata"]["annotations"] == annotations


def test_target_refs_can_be_configured_and_default(
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    service_name = random_string()
    explicit_name = random_string()
    target_refs = {
        "explicit": {
            "group": "",
            "kind": "Service",
            "name": explicit_name,
            "sectionName": "https",
        },
        "defaulted": {},
    }
    values = {
        "backendTLSPolicies": {
            "identifier": {"targetRefs": target_refs},
        },
        "service": {"name": service_name},
    }
    subject = render_subjects(helm_runner=helm_runner, values=values)[0]
    assert subject["kind"] == "BackendTLSPolicy"

    expected_service_name = helper_renderer.render(
        "service-name",
        values={"service": {"name": service_name}},
    )

    rendered = subject["spec"]["targetRefs"]
    assert len(rendered) == len(target_refs)
    by_name = {ref["name"]: ref for ref in rendered}

    explicit = by_name[explicit_name]
    assert explicit["group"] == ""
    assert explicit["kind"] == "Service"
    assert explicit["sectionName"] == "https"

    # The default targetRef resolves its name to this chart's service, defaults
    # its kind to Service and its group to the core ("") group, and omits
    # sectionName when not provided.
    defaulted = by_name[expected_service_name]
    assert defaulted["group"] == ""
    assert defaulted["kind"] == "Service"
    assert "sectionName" not in defaulted


def test_validation_is_passed_through(helm_runner: HelmRunner) -> None:
    validation = {
        "wellKnownCACertificates": "System",
        "hostname": "backend.example.com",
        "subjectAltNames": [
            {"type": "Hostname", "hostname": "backend.example.com"},
        ],
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTLSPolicies": {
                "identifier": {"validation": validation},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTLSPolicy"
    assert subject["spec"]["validation"] == validation


def test_validation_can_be_omitted(helm_runner: HelmRunner) -> None:
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTLSPolicies": {
                "identifier": {"validation": None},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTLSPolicy"
    assert "validation" not in subject["spec"]


def render_subjects(
    helm_runner: HelmRunner,
    name: Optional[str] = None,
    values: Optional[Dict] = None,
) -> List[Dict]:
    _name = name or random_string()
    _values = random_required_values() | (values or {})

    default_policy_values = {
        "create": True,
        "targetRefs": {
            random_string(): {},
        },
        "validation": {
            "wellKnownCACertificates": "System",
            "hostname": "example.private.example.com",
        },
    }
    policies_values = cast(
        Dict[str, Dict], _values.get("backendTLSPolicies") or {"identifier": {}}
    )
    _values["backendTLSPolicies"] = {
        key: (default_policy_values | policy_values)
        for key, policy_values in policies_values.items()
    }

    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/backend_tls_policies.yaml"],
        values=[_values],
    )
    return manifests
