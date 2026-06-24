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


def test_persistent_volume_claim_is_omitted_by_default(helm_runner: HelmRunner) -> None:
    resources = helm_runner.template(
        chart=CHART_NAME,
        name="any-name",
        values=[random_required_values()],
    )
    assert len(resources) > 0
    assert all(
        resource.get("kind") != "PersistentVolumeClaim" for resource in resources
    )


def test_resource_is_omitted_when_create_is_false(helm_runner: HelmRunner) -> None:
    values = random_required_values() | {
        "persistentVolumeClaims": {
            "snapshots": {
                "create": False,
                "spec": {"accessModes": ["ReadWriteOnce"]},
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
        resource.get("kind") != "PersistentVolumeClaim" for resource in resources
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

    assert subject["apiVersion"] == "v1"
    assert subject["kind"] == "PersistentVolumeClaim"

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
    # Name defaults to <full-name>-<identifier> so a referencing claimName stays
    # stable across releases.
    assert metadata["name"] == f"{default_full_name}-snapshots"
    assert "annotations" not in metadata


def test_name_can_be_overridden_with_the_name_value(helm_runner: HelmRunner) -> None:
    name = random_string()
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "persistentVolumeClaims": {
                "snapshots": {"name": name},
            },
        },
    )[0]
    assert subject["kind"] == "PersistentVolumeClaim"
    assert subject["metadata"]["name"] == name


def test_annotations_can_be_configured_with_the_annotations_value(
    helm_runner: HelmRunner,
) -> None:
    annotations = EXAMPLE_MAPPING
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "persistentVolumeClaims": {
                "snapshots": {"annotations": annotations},
            },
        },
    )[0]
    assert subject["kind"] == "PersistentVolumeClaim"
    assert subject["metadata"]["annotations"] == annotations


def test_spec_is_passed_through(helm_runner: HelmRunner) -> None:
    spec = {
        "accessModes": ["ReadWriteOnce"],
        "storageClassName": "local-path-bulk",
        "resources": {"requests": {"storage": "5Gi"}},
    }
    subject = render_subjects(
        helm_runner=helm_runner,
        values={
            "persistentVolumeClaims": {
                "snapshots": {"spec": spec},
            },
        },
    )[0]
    assert subject["kind"] == "PersistentVolumeClaim"
    assert subject["spec"] == spec


def render_subjects(
    helm_runner: HelmRunner,
    name: Optional[str] = None,
    values: Optional[Dict] = None,
) -> List[Dict]:
    _name = name or random_string()
    _values = random_required_values() | (values or {})

    default_pvc_values = {
        "create": True,
        "spec": {
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": "1Gi"}},
        },
    }
    pvc_values = cast(
        Dict[str, Dict], _values.get("persistentVolumeClaims") or {"snapshots": {}}
    )
    _values["persistentVolumeClaims"] = {
        key: (default_pvc_values | pvc) for key, pvc in pvc_values.items()
    }

    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/persistent_volume_claims.yaml"],
        values=[_values],
    )
    return manifests
