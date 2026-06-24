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


def test_backend_traffic_policy_resource_is_omitted_by_default(
    helm_runner: HelmRunner,
) -> None:
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[random_required_values()],
    )
    assert len(resources) > 0
    assert all(
        [resource.get("kind") != "BackendTrafficPolicy" for resource in resources]
    )


def test_resource_is_omitted_when_create_is_false(helm_runner: HelmRunner) -> None:
    values = random_required_values() | {
        "backendTrafficPolicies": {
            "identifier": {
                "create": False,
                "targetRefs": {"route": {}},
                "spec": {"timeout": {"http": {"requestTimeout": "300s"}}},
            },
        },
    }
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[values],
    )
    assert len(resources) > 0
    assert all(
        [resource.get("kind") != "BackendTrafficPolicy" for resource in resources]
    )


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

    assert subject["kind"] == "BackendTrafficPolicy"

    default_api_version = helper_renderer.render(
        helper_name="backend-traffic-policy-api-version",
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


def test_api_version_defaults_to_envoy_gateway_v1alpha1(
    helm_runner: HelmRunner,
) -> None:
    subject = render_subjects(helm_runner=helm_runner)[0]
    assert subject["apiVersion"] == "gateway.envoyproxy.io/v1alpha1"


def test_api_version_can_be_set_with_global_gateway_api_value(
    helm_runner: HelmRunner,
) -> None:
    api_version = "gateway.envoyproxy.io/v1alpha2"
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "global": {"gatewayApi": {"backendTrafficPolicyApiVersion": api_version}}
        },
    )[0]
    assert subject["apiVersion"] == api_version


def test_name_can_be_overridden_with_the_name_value(helm_runner: HelmRunner) -> None:
    name = random_string()
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTrafficPolicies": {
                "identifier": {"name": name},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTrafficPolicy"
    assert subject["metadata"]["name"] == name


def test_annotations_can_be_configured_with_the_annotations_value(
    helm_runner: HelmRunner,
) -> None:
    annotations = EXAMPLE_MAPPING
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTrafficPolicies": {
                "identifier": {"annotations": annotations},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTrafficPolicy"
    assert subject["metadata"]["annotations"] == annotations


def test_target_refs_can_be_configured_and_default(
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    explicit_name = random_string()
    target_refs = {
        "explicit": {
            "group": "gateway.networking.k8s.io",
            "kind": "HTTPRoute",
            "name": explicit_name,
        },
        "defaulted": {},
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        name=release_name,
        values={
            "appName": EXAMPLE_APP_NAME,
            "backendTrafficPolicies": {
                "identifier": {"targetRefs": target_refs},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTrafficPolicy"

    expected_full_name = helper_renderer.render(
        "full-name",
        name=release_name,
        values={"appName": EXAMPLE_APP_NAME},
    )

    rendered = subject["spec"]["targetRefs"]
    assert len(rendered) == len(target_refs)
    by_name = {ref["name"]: ref for ref in rendered}

    explicit = by_name[explicit_name]
    assert explicit["group"] == "gateway.networking.k8s.io"
    assert explicit["kind"] == "HTTPRoute"

    # The default targetRef resolves its name to this chart's full-name and
    # defaults its kind to HTTPRoute and group to the Gateway API group.
    defaulted = by_name[expected_full_name]
    assert defaulted["group"] == "gateway.networking.k8s.io"
    assert defaulted["kind"] == "HTTPRoute"


def test_spec_is_passed_through(helm_runner: HelmRunner) -> None:
    spec = {
        "timeout": {"http": {"requestTimeout": "300s"}},
        "retry": {"numRetries": 3},
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTrafficPolicies": {
                "identifier": {"spec": spec},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTrafficPolicy"
    rendered_spec = subject["spec"]
    assert rendered_spec["timeout"] == spec["timeout"]
    assert rendered_spec["retry"] == spec["retry"]


def test_spec_can_be_omitted(helm_runner: HelmRunner) -> None:
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "backendTrafficPolicies": {
                "identifier": {"spec": None},
            },
        },
    )[0]
    assert subject["kind"] == "BackendTrafficPolicy"
    # Only the templated targetRefs remain in the spec when no passthrough is set.
    assert list(subject["spec"].keys()) == ["targetRefs"]


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
        "spec": {
            "timeout": {"http": {"requestTimeout": "300s"}},
        },
    }
    policies_values = cast(
        Dict[str, Dict], _values.get("backendTrafficPolicies") or {"identifier": {}}
    )
    _values["backendTrafficPolicies"] = {
        key: (default_policy_values | policy_values)
        for key, policy_values in policies_values.items()
    }

    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/backend_traffic_policies.yaml"],
        values=[_values],
    )
    return manifests
