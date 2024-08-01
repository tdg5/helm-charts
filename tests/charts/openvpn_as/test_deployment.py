from typing import Dict, Optional

from pytest_helm_templates import HelmRunner


def test_constant_and_default_values(
    app_version: str,
    chart_name: str,
    chart_values: Dict,
    chart_version: str,
    helm_runner: HelmRunner,
) -> None:
    name = "release-name"
    subject = render_subject(
        helm_runner=helm_runner,
        name=name,
    )
    assert "Deployment" == subject["kind"]
    assert "apps/v1" == subject["apiVersion"]

    metadata = subject["metadata"]
    assert metadata
    assert metadata["name"] == f"{name}-{chart_name}"
    assert "annotations" not in metadata

    labels = metadata["labels"]
    assert labels["app.kubernetes.io/instance"] == name
    assert labels["app.kubernetes.io/managed-by"] == "Helm"
    assert labels["app.kubernetes.io/name"] == chart_name
    assert labels["app.kubernetes.io/version"] == app_version
    assert labels["helm.sh/chart"] == f"{chart_name}-{chart_version}"

    spec = subject["spec"]
    assert spec
    assert spec["replicas"] == 1

    selector = spec["selector"]
    assert selector
    match_labels = selector["matchLabels"]
    assert match_labels["app.kubernetes.io/name"] == chart_name
    assert match_labels["app.kubernetes.io/instance"] == name

    strategy = spec["strategy"]
    assert strategy
    assert strategy["type"] == "Recreate"

    template = spec["template"]
    assert template

    template_metadata = template["metadata"]
    assert template_metadata

    annotations = template_metadata["annotations"]
    assert annotations


def render_subject(
    helm_runner: HelmRunner,
    name: str = "name-given-to-the-release",
    values: Optional[Dict] = None,
) -> Dict:
    manifests = helm_runner.template(
        chart="openvpn-as",
        name=name,
        show_only=["templates/deployment.yaml"],
        values=[values] if values else [],
    )
    subject = manifests[0]
    assert subject["kind"] == "Deployment"
    return subject
