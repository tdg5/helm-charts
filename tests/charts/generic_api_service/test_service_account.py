from typing import Dict, Optional

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


def test_service_account_resource_can_be_omitted(helm_runner: HelmRunner) -> None:
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[random_required_values() | {"serviceAccount": {"create": False}}],
    )
    assert len(resources) > 0
    assert all(resource.get("kind") != "ServiceAccount" for resource in resources)


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
    assert subject["automountServiceAccountToken"] == (
        chart_values["serviceAccount"]["automount"]
    )
    assert subject["kind"] == "ServiceAccount"

    metadata = subject["metadata"]

    assert "annotations" not in metadata
    assert "namespace" not in metadata

    default_labels_yaml = helper_renderer.render(
        "labels",
        name=release_name,
        values=values,
    )
    default_labels = yaml.safe_load(default_labels_yaml)
    assert metadata["labels"] == default_labels

    default_service_account_name = helper_renderer.render(
        "service-account-name",
        name=release_name,
        values=values,
    )
    assert metadata["name"] == default_service_account_name


def test_automount_service_account_token_can_be_customized_with_service_account_automount_value(  # noqa: E501
    helm_runner: HelmRunner,
) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"serviceAccount": {"automount": False}},
    )
    assert subject["automountServiceAccountToken"] is False


def test_annotations_can_be_specified_with_service_account_annotations_value(
    helm_runner: HelmRunner,
) -> None:
    annotations = EXAMPLE_MAPPING
    subject = render_subject(
        helm_runner=helm_runner,
        values={"serviceAccount": {"annotations": annotations}},
    )

    assert subject["metadata"]["annotations"] == annotations


def test_annotations_can_be_omitted(helm_runner: HelmRunner) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"serviceAccount": {"annotations": None}},
    )

    assert "annotations" not in subject["metadata"]


def test_labels_can_be_added_with_service_account_labels_value(
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    labels = EXAMPLE_MAPPING
    values = {
        "appName": EXAMPLE_APP_NAME,
        "appVersion": EXAMPLE_APP_VERSION,
        "serviceAccount": {"labels": labels},
    }
    subject = render_subject(
        helm_runner=helm_runner,
        name=release_name,
        values=values,
    )

    default_labels_yaml = helper_renderer.render(
        "labels",
        name=release_name,
        values=values,
    )
    default_labels = yaml.safe_load(default_labels_yaml)
    expected_labels = default_labels | labels

    assert subject["metadata"]["labels"] == expected_labels


def render_subject(
    helm_runner: HelmRunner,
    name: Optional[str] = None,
    values: Dict = {},
) -> Dict:
    _name = name or random_string()
    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/service_account.yaml"],
        values=[random_required_values() | values],
    )
    subject = manifests[0]
    assert subject["kind"] == "ServiceAccount"
    return subject
