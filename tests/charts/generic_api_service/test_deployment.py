from typing import Any, Dict, List, Optional, cast

import pytest
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


def test_static_values_and_defaults(
    chart_values: Dict,
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    app_name = EXAMPLE_APP_NAME
    app_version = EXAMPLE_APP_VERSION
    values = {"appName": app_name, "appVersion": app_version}
    subject = render_subject(
        helm_runner=helm_runner,
        name=release_name,
        values=values,
    )

    assert subject["apiVersion"] == "apps/v1"
    assert subject["kind"] == "Deployment"

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

    spec = subject["spec"]
    assert spec["replicas"] == chart_values["replicaCount"]
    assert spec["revisionHistoryLimit"] == 5
    # strategy is omitted by default, leaving the Kubernetes default.
    assert "strategy" not in spec

    default_selector_labels_yaml = helper_renderer.render(
        "selector-labels",
        name=release_name,
        values=values,
    )
    default_selector_labels = yaml.safe_load(default_selector_labels_yaml)

    selector = spec["selector"]
    assert selector["matchLabels"] == default_selector_labels

    template = spec["template"]

    template_metadata = template["metadata"]
    assert template_metadata
    assert "annotations" not in template_metadata
    assert template_metadata["labels"] == default_labels

    template_spec = template["spec"]
    assert "affinity" not in template_spec

    containers = template_spec["containers"]
    assert len(containers) == 1

    container_values = chart_values["container"]

    container = containers[0]
    # Image should be there, but for this test it will have random values.
    assert "image" in container

    assert container["imagePullPolicy"] == container_values["image"]["pullPolicy"]

    liveness_probe = container["livenessProbe"]
    assert liveness_probe == container_values["livenessProbe"]

    assert container["name"] == app_name

    ports = container["ports"]
    assert len(ports) == 1

    expected_ports_by_name = {
        port["name"]: {
            "containerPort": port["containerPort"],
            "name": port["name"],
            "protocol": port["protocol"],
        }
        for port in chart_values["ports"].values()
    }
    ports_by_name = {port["name"]: port for port in ports}

    assert ports_by_name == expected_ports_by_name

    readiness_probe = container["readinessProbe"]
    assert readiness_probe == container_values["readinessProbe"]

    assert "resources" not in container
    assert "securityContext" not in container
    assert "startupProbe" not in container
    assert "volumeMounts" not in container

    assert "imagePullSecrets" not in template_spec
    assert "nodeSelector" not in template_spec

    default_service_account_name = helper_renderer.render(
        "service-account-name",
        name=release_name,
        values=values,
    )
    assert template_spec["serviceAccountName"] == default_service_account_name

    assert "securityContext" not in template_spec
    assert "tolerations" not in template_spec
    assert "volumes" not in template_spec


def test_replicas_can_be_customized_by_setting_appropriate_value(
    chart_values: Dict,
    helm_runner: HelmRunner,
) -> None:
    replica_count = 42
    assert replica_count != chart_values["replicaCount"]
    subject = render_subject(
        helm_runner=helm_runner,
        values={"replicaCount": replica_count},
    )

    assert subject["spec"]["replicas"] == replica_count


def test_revision_history_limit_can_be_customized_by_setting_appropriate_value(
    chart_values: Dict,
    helm_runner: HelmRunner,
) -> None:
    revision_history_limit_count = 42
    assert revision_history_limit_count != chart_values.get("revisionHistoryLimit")
    subject = render_subject(
        helm_runner=helm_runner,
        values={"revisionHistoryLimit": revision_history_limit_count},
    )

    assert subject["spec"]["revisionHistoryLimit"] == revision_history_limit_count


def test_strategy_is_omitted_by_default(helm_runner: HelmRunner) -> None:
    subject = render_subject(helm_runner=helm_runner)
    assert "strategy" not in subject["spec"]


def test_strategy_can_be_set_with_the_strategy_value(helm_runner: HelmRunner) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"strategy": {"type": "Recreate"}},
    )
    assert subject["spec"]["strategy"] == {"type": "Recreate"}


@pytest.mark.parametrize("expected_annotations", [None, EXAMPLE_MAPPING])
def test_pod_annotations_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    expected_annotations: Optional[Dict[str, Any]],
) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"pod": {"annotations": expected_annotations}},
    )

    annotations = subject["spec"]["template"]["metadata"].get("annotations")
    assert annotations == expected_annotations


def test_additional_pod_labels_can_be_customized_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    app_name = EXAMPLE_APP_NAME
    app_version = EXAMPLE_APP_VERSION
    release_name = EXAMPLE_RELEASE_NAME
    expected_extra_labels = EXAMPLE_MAPPING
    values = {
        "appName": app_name,
        "appVersion": app_version,
        "pod": {
            "labels": expected_extra_labels,
        },
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
    expected_labels = default_labels | expected_extra_labels

    pod_labels = subject["spec"]["template"]["metadata"]["labels"]
    assert pod_labels == expected_labels


@pytest.mark.parametrize("expected_affinity", [None, EXAMPLE_MAPPING])
def test_affinity_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    expected_affinity: Optional[Dict[str, Any]],
) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"pod": {"affinity": expected_affinity}},
    )

    affinity = subject["spec"]["template"]["spec"].get("affinity")
    assert affinity == expected_affinity


@pytest.mark.parametrize("expected_env", [None, EXAMPLE_MAPPING])
def test_container_env_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
    expected_env: Dict[str, Any],
) -> None:
    app_name = EXAMPLE_APP_NAME
    values = random_required_values
    values["appName"] = app_name
    _env = {"env-id": expected_env} if expected_env else None
    values["container"]["env"] = _env
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    env = container.get("env")

    if env:
        assert len(env) == 1
        assert env[0] == expected_env
    else:
        assert env is None


def test_image_repository_can_be_customized_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
) -> None:
    app_name = EXAMPLE_APP_NAME
    image_repository = "image-repository"
    image_tag = random_string()
    values = random_required_values
    values["appName"] = app_name
    values["container"]["image"]["repository"] = image_repository
    values["container"]["image"]["tag"] = image_tag
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    assert container["image"] == f"{image_repository}:{image_tag}"


def test_image_tag_can_be_customized_by_setting_appropriate_value(
    helm_runner: HelmRunner, random_required_values: Dict[str, Any]
) -> None:
    app_name = EXAMPLE_APP_NAME
    image_repository = random_string()
    image_tag = "image-tag"
    values = random_required_values
    values["appName"] = app_name
    values["container"]["image"]["repository"] = image_repository
    values["container"]["image"]["tag"] = image_tag
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    assert container["image"] == f"{image_repository}:{image_tag}"


def test_image_pull_policy_can_be_customized_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
) -> None:
    app_name = EXAMPLE_APP_NAME
    image_pull_policy = "Never"
    values = random_required_values
    values["appName"] = app_name
    values["container"]["image"]["pullPolicy"] = image_pull_policy
    subject = render_subject(
        helm_runner=helm_runner,
        values=values,
    )

    container = get_container_by_name(app_name, subject)
    assert container["imagePullPolicy"] == image_pull_policy


@pytest.mark.parametrize("expected_liveness_probe", [None, {"grpc": {"port": 2379}}])
def test_liveness_probe_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
    expected_liveness_probe: Optional[Dict[str, Any]],
) -> None:
    values = random_required_values
    app_name = EXAMPLE_APP_NAME
    _liveness_probe = (
        expected_liveness_probe | {"httpGet": None} if expected_liveness_probe else None
    )
    values["appName"] = app_name
    values["container"]["livenessProbe"] = _liveness_probe
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    assert container.get("livenessProbe") == expected_liveness_probe


def test_ports_can_be_customized_by_setting_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    app_name = EXAMPLE_APP_NAME
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
        values={"appName": app_name, "ports": ports},
    )

    container = get_container_by_name(app_name, subject)
    container_ports_by_name = {port["name"]: port for port in container["ports"]}
    assert "http" not in container_ports_by_name

    container_new_port = container_ports_by_name["new"]
    assert container_new_port["containerPort"] == new_port["containerPort"]
    assert container_new_port["name"] == new_port["name"]
    assert container_new_port["protocol"] == new_port["protocol"]
    assert "servicePort" not in container_new_port


def test_ports_can_be_omitted(
    helm_runner: HelmRunner,
) -> None:
    app_name = EXAMPLE_APP_NAME
    subject = render_subject(
        helm_runner=helm_runner,
        values={"appName": app_name, "ports": None},
    )

    container = get_container_by_name(app_name, subject)
    assert "ports" not in container


@pytest.mark.parametrize("expected_readiness_probe", [None, {"grpc": {"port": 2379}}])
def test_readiness_probe_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
    expected_readiness_probe: Optional[Dict[str, Any]],
) -> None:
    app_name = EXAMPLE_APP_NAME
    values = random_required_values
    _readiness_probe = (
        expected_readiness_probe | {"httpGet": None}
        if expected_readiness_probe
        else None
    )
    values["appName"] = EXAMPLE_APP_NAME
    values["container"]["readinessProbe"] = _readiness_probe
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    assert container.get("readinessProbe") == expected_readiness_probe


@pytest.mark.parametrize("expected_resources", [None, EXAMPLE_MAPPING])
def test_resources_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
    expected_resources: Optional[Dict[str, Any]],
) -> None:
    app_name = EXAMPLE_APP_NAME
    values = random_required_values
    values["appName"] = app_name
    values["container"]["resources"] = expected_resources
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    assert container.get("resources") == expected_resources


@pytest.mark.parametrize("expected_security_context", [None, EXAMPLE_MAPPING])
def test_container_security_context_can_be_customized_or_omitted_by_setting_appropriate_value(  # noqa: E501
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
    expected_security_context: Optional[Dict[str, Any]],
) -> None:
    values = random_required_values
    app_name = EXAMPLE_APP_NAME
    values["container"]["securityContext"] = expected_security_context
    values["appName"] = app_name
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    assert container.get("securityContext") == expected_security_context


@pytest.mark.parametrize(
    "expected_startup_probe", [None, {"httpGet": {"grpc": {"port": 2379}}}]
)
def test_startup_probe_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
    expected_startup_probe: Optional[Dict[str, Any]],
) -> None:
    app_name = EXAMPLE_APP_NAME
    values = random_required_values
    _startup_probe = expected_startup_probe if expected_startup_probe else None
    values["appName"] = EXAMPLE_APP_NAME
    values["container"]["startupProbe"] = _startup_probe
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    assert container.get("startupProbe") == expected_startup_probe


@pytest.mark.parametrize("expected_volume_mount", [None, EXAMPLE_MAPPING])
def test_volume_mounts_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    random_required_values: Dict[str, Any],
    expected_volume_mount: Optional[Dict[str, Any]],
) -> None:
    values = random_required_values
    app_name = EXAMPLE_APP_NAME
    values["appName"] = app_name
    values["container"]["volumeMounts"] = (
        {"volume-mount-id": expected_volume_mount} if expected_volume_mount else None
    )
    subject = render_subject(helm_runner=helm_runner, values=values)

    container = get_container_by_name(app_name, subject)
    volume_mounts = container.get("volumeMounts")

    if expected_volume_mount:
        _volume_mounts = cast(List[Dict[str, Any]], volume_mounts)
        assert len(_volume_mounts) == 1
        assert _volume_mounts[0] == expected_volume_mount
    else:
        assert volume_mounts is None


@pytest.mark.parametrize(
    "expected_image_pull_secrets",
    [None, {"one": "one", "two": "two", "arbitrary": "three"}],
)
def test_image_pull_secrets_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    expected_image_pull_secrets: Optional[Dict[str, str]],
) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"pod": {"imagePullSecrets": expected_image_pull_secrets}},
    )

    image_pull_secrets = subject["spec"]["template"]["spec"].get("imagePullSecrets")

    if expected_image_pull_secrets:
        expected_image_pull_secret_values = set(expected_image_pull_secrets.values())

        # Order sometimes varies.
        for image_pull_secret in image_pull_secrets:
            assert image_pull_secret in expected_image_pull_secret_values
    else:
        assert image_pull_secrets is None


@pytest.mark.parametrize("expected_node_selector", [None, EXAMPLE_MAPPING])
def test_node_selector_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    expected_node_selector: Optional[Dict[str, Any]],
) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"pod": {"nodeSelector": expected_node_selector}},
    )

    node_selector = subject["spec"]["template"]["spec"].get("nodeSelector")
    assert node_selector == expected_node_selector


@pytest.mark.parametrize("expected_security_context", [None, EXAMPLE_MAPPING])
def test_security_context_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    expected_security_context: Optional[Dict[str, Any]],
) -> None:
    subject = render_subject(
        helm_runner=helm_runner,
        values={"pod": {"securityContext": expected_security_context}},
    )

    security_context = subject["spec"]["template"]["spec"].get("securityContext")
    assert security_context == expected_security_context


@pytest.mark.parametrize("expected_toleration", [None, EXAMPLE_MAPPING])
def test_tolerations_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    expected_toleration: Optional[Dict[str, Any]],
) -> None:
    _tolerations = (
        {"toleration-id": expected_toleration} if expected_toleration else None
    )
    subject = render_subject(
        helm_runner=helm_runner,
        values={"pod": {"tolerations": _tolerations}},
    )

    tolerations = subject["spec"]["template"]["spec"].get("tolerations")
    if expected_toleration:
        assert len(tolerations) == 1
        assert tolerations[0] == expected_toleration
    else:
        assert tolerations is None


@pytest.mark.parametrize("expected_volume", [None, EXAMPLE_MAPPING])
def test_volumes_can_be_customized_or_omitted_by_setting_appropriate_value(
    helm_runner: HelmRunner,
    expected_volume: Optional[Dict[str, Any]],
) -> None:
    volume_identifier = "volume-id"
    _volumes = {volume_identifier: expected_volume} if expected_volume else None
    subject = render_subject(
        helm_runner=helm_runner,
        values={"pod": {"volumes": _volumes}},
    )

    volumes = subject["spec"]["template"]["spec"].get("volumes")
    if expected_volume:
        assert len(volumes) == 1
        assert volumes[0] == expected_volume
    else:
        assert volumes is None


def get_container_by_name(
    container_name: str,
    manifest: Dict[str, Any],
) -> Dict[str, Any]:
    containers = manifest["spec"]["template"]["spec"]["containers"]
    for container in containers:
        if container["name"] == container_name and isinstance(container, Dict):
            return container

    raise RuntimeError(f"Could not find container with name {container_name}")


def render_subject(
    helm_runner: HelmRunner,
    name: Optional[str] = None,
    values: Dict = {},
) -> Dict:
    _name = name or random_string()
    manifests = helm_runner.template(
        chart=CHART_NAME,
        name=_name,
        show_only=["templates/deployment.yaml"],
        values=[random_required_values() | values],
    )
    subject = manifests[0]
    assert subject["kind"] == "Deployment"
    return subject
