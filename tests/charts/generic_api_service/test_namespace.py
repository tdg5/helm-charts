from typing import Dict, Optional

from pytest_helm_templates import HelmRunner

from tests.charts.generic_api_service import CHART_NAME, random_required_values
from tests.test_helpers import HelperRenderer, random_string
from tests.test_helpers.test_constants import EXAMPLE_RELEASE_NAME


def test_static_values_and_defaults(
    chart_values: Dict,
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    subject = render_subject(
        helm_runner=helm_runner,
        name=release_name,
    )

    assert subject["apiVersion"] == "v1"
    assert subject["kind"] == "Namespace"

    metadata = subject["metadata"]

    # Name is expected to be there, but is random for this test.
    assert "name" in metadata
    assert "labels" not in metadata


def test_namespace_resource_can_be_omitted(helm_runner: HelmRunner) -> None:
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[random_required_values() | {"namespace": {"create": False}}],
    )
    assert len(resources) > 0
    assert all(resource.get("kind") != "Namespace" for resource in resources)


def test_name_can_be_configured_with_namespace_name(
    helm_runner: HelmRunner,
) -> None:
    expected_namespace_name = "namespace-name"
    subject = render_subject(
        helm_runner=helm_runner,
        values={"namespace": {"name": expected_namespace_name}},
    )
    assert subject["metadata"]["name"] == expected_namespace_name


def test_labels_can_be_specified(
    chart_values: Dict,
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    label_name = "label_name"
    label_value = "label_value"
    subject = render_subject(
        helm_runner=helm_runner,
        name=release_name,
        values={"namespace": {"labels": {label_name: label_value}}},
    )

    metadata = subject["metadata"]
    assert "labels" in metadata
    labels = metadata["labels"]
    assert label_name in labels
    assert labels[label_name] == label_value


def render_subject(
    helm_runner: HelmRunner,
    name: Optional[str] = None,
    values: Dict = {},
) -> Dict:
    _name = name or random_string()
    default_namespace_values = {
        "create": True,
        "name": random_string(),
    }
    _values = random_required_values() | values
    namespace_values = _values.get("namespace", {})
    _values["namespace"] = default_namespace_values | namespace_values
    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/namespace.yaml"],
        values=[_values],
    )
    subject = manifests[0]
    assert subject["kind"] == "Namespace"
    return subject
