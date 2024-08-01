from typing import Dict, List, Optional

from pytest_helm_templates import HelmRunner

from tests.test_helpers import HelperRenderer, factories


EXAMPLE_MAPPING = factories.dict_with_keys_of_string_and_values_of_any()

EXAMPLE_LIST = list(EXAMPLE_MAPPING.keys())


def test_constant_and_default_values(
    app_version: str,
    chart_name: str,
    chart_values: Dict,
    chart_version: str,
    helm_runner: HelmRunner,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = "release-name"
    subject = render_subject(
        helm_runner=helm_runner,
        name=release_name,
    )
    assert "Deployment" == subject["kind"]
    assert "apps/v1" == subject["apiVersion"]

    full_name_helper_result = helper_renderer.render("full-name", name=release_name)

    metadata = subject["metadata"]
    assert metadata
    assert metadata["name"] == full_name_helper_result
    assert "annotations" not in metadata

    chart_helper_result = helper_renderer.render("chart", name=release_name)

    labels = metadata["labels"]
    assert labels["app.kubernetes.io/instance"] == release_name
    assert labels["app.kubernetes.io/managed-by"] == "Helm"
    assert labels["app.kubernetes.io/name"] == chart_name
    assert labels["app.kubernetes.io/version"] == app_version
    assert labels["helm.sh/chart"] == chart_helper_result

    spec = subject["spec"]
    assert spec
    assert spec["replicas"] == chart_values.get("replicaCount", 1)

    selector = spec["selector"]
    assert selector
    match_labels = selector["matchLabels"]
    assert match_labels["app.kubernetes.io/name"] == chart_name
    assert match_labels["app.kubernetes.io/instance"] == release_name

    template = spec["template"]
    assert template

    template_metadata = template["metadata"]
    assert template_metadata

    template_labels = template_metadata["labels"]
    assert template_labels
    assert template_labels["app.kubernetes.io/name"] == chart_name
    assert template_labels["app.kubernetes.io/instance"] == release_name
    assert "annotations" not in template_metadata

    pod_spec = template["spec"]
    assert "affinity" not in pod_spec

    containers = pod_spec["containers"]
    assert containers
    assert len(containers) == 1

    container = containers[0]
    container_env = container["env"]
    assert container_env

    expected_env_variables = [
        {"name": "TZ", "value": "Etc/UTC"},
    ]
    assert len(container_env) == len(expected_env_variables)

    env_variables_by_name = {
        env_variable["name"]: env_variable for env_variable in container_env
    }

    for expected_env_variable in expected_env_variables:
        env_variable = env_variables_by_name[expected_env_variable["name"]]
        assert env_variable == expected_env_variable

    image = container["image"]
    assert image
    image_repository = chart_values["image"]["repository"]
    image_tag = chart_values["image"].get("tag") or app_version
    assert image == f"{image_repository}:{image_tag}"

    assert container["imagePullPolicy"] == chart_values["image"]["pullPolicy"]

    assert container["name"] == chart_name

    ports = container["ports"]
    assert ports
    assert len(ports) == 3

    expected_ports: List[Dict[str, str]] = [
        {
            "containerPort": chart_values["service"]["vpnTcpPort"],
            "name": "vpn-tcp",
            "protocol": "TCP",
        },
        {
            "containerPort": chart_values["service"]["vpnUdpPort"],
            "name": "vpn-udp",
            "protocol": "UDP",
        },
        {
            "containerPort": chart_values["service"]["vpnUiPort"],
            "name": "vpn-ui",
            "protocol": "TCP",
        },
    ]

    ports_by_name = {port["name"]: port for port in ports}
    for expected_port in expected_ports:
        port = ports_by_name[expected_port["name"]]
        assert port == expected_port

    liveness_probe = container["livenessProbe"]
    assert liveness_probe["exec"]["command"] == (
        ["/usr/local/openvpn_as/scripts/sacli", "Status"]
    )
    assert liveness_probe["initialDelaySeconds"] == 100
    assert liveness_probe["timeoutSeconds"] == 5

    readiness_probe = container["readinessProbe"]
    assert readiness_probe["initialDelaySeconds"] == 100
    assert readiness_probe["tcpSocket"]["port"] == chart_values["service"]["vpnUiPort"]

    assert "resources" not in container

    security_context = container.get("securityContext")
    assert security_context == chart_values["securityContext"]

    volume_mounts = container["volumeMounts"]
    assert volume_mounts

    expected_volume_mounts = [
        {"mountPath": "/openvpn", "name": "persistence"},
    ]
    assert len(volume_mounts) == len(expected_volume_mounts)

    volume_mounts_by_name = {
        volume_mount["name"]: volume_mount for volume_mount in volume_mounts
    }
    for expected_volume_mount in expected_volume_mounts:
        volume_mount = volume_mounts_by_name[expected_volume_mount["name"]]
        assert volume_mount == expected_volume_mount

    assert "imagePullSecrets" not in pod_spec
    assert "nodeSelector" not in pod_spec

    service_account_name_helper_result = helper_renderer.render(
        "service-account-name", name=release_name
    )

    assert pod_spec["serviceAccountName"] == service_account_name_helper_result

    assert "securityContext" not in pod_spec
    assert "tolerations" not in pod_spec

    volumes = pod_spec["volumes"]
    assert volumes

    expected_volumes = [
        {
            "name": "persistence",
            "persistentVolumeClaim": {
                "claimName": f"{full_name_helper_result}-data",
            },
        }
    ]

    assert len(volumes) == len(expected_volumes)

    volumes_by_name = {volume["name"]: volume for volume in volumes}

    for expected_volume in expected_volumes:
        volume = volumes_by_name[expected_volume["name"]]
        assert volume == expected_volume


def test_deployment_name_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    full_name_override = "full-name-override"
    subject = render_subject(
        helm_runner=helm_runner,
        values={"fullNameOverride": full_name_override},
    )
    assert subject["metadata"]["name"] == full_name_override


def test_replicas_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    replica_count = 42
    subject = render_subject(
        helm_runner=helm_runner,
        values={"replicaCount": replica_count},
    )
    assert subject["spec"]["replicas"] == replica_count


def test_replicas_defaults_to_one_when_empty_value_given(
    helm_runner: HelmRunner,
) -> None:
    for empty_value in [0, None, ""]:
        subject = render_subject(
            helm_runner=helm_runner,
            values={"replicaCount": empty_value},
        )
        assert subject["spec"]["replicas"] == 1


def test_pod_annotations_can_be_specified_or_omitted_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_MAPPING
        subject = render_subject(
            helm_runner=helm_runner,
            values={"podAnnotations": value},
        )
        metadata = subject["spec"]["template"]["metadata"]
        if should_omit:
            assert "annotations" not in metadata
        else:
            assert metadata["annotations"] == value


def test_affinity_can_be_specified_or_omitted_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_MAPPING
        subject = render_subject(
            helm_runner=helm_runner,
            values={"affinity": value},
        )
        pod_spec = subject["spec"]["template"]["spec"]
        if should_omit:
            assert "affinity" not in pod_spec
        else:
            assert pod_spec["affinity"] == value


def test_image_pull_secrets_can_be_specified_or_omitted_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_LIST
        subject = render_subject(
            helm_runner=helm_runner,
            values={"imagePullSecrets": value},
        )
        pod_spec = subject["spec"]["template"]["spec"]
        if should_omit:
            assert "imagePullSecrets" not in pod_spec
        else:
            assert pod_spec["imagePullSecrets"] == value


def test_node_selector_can_be_specified_or_omitted_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_MAPPING
        subject = render_subject(
            helm_runner=helm_runner,
            values={"nodeSelector": value},
        )
        pod_spec = subject["spec"]["template"]["spec"]
        if should_omit:
            assert "nodeSelector" not in pod_spec
        else:
            assert pod_spec["nodeSelector"] == value


def test_pod_security_context_can_be_specified_or_omitted_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_MAPPING
        subject = render_subject(
            helm_runner=helm_runner,
            values={"podSecurityContext": value},
        )
        pod_spec = subject["spec"]["template"]["spec"]
        if should_omit:
            assert "securityContext" not in pod_spec
        else:
            assert pod_spec["securityContext"] == value


def test_service_account_name_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    service_account_name = factories.random_string()
    subject = render_subject(
        helm_runner=helm_runner,
        values={"serviceAccount": {"name": service_account_name}},
    )
    pod_spec = subject["spec"]["template"]["spec"]
    assert pod_spec["serviceAccountName"] == service_account_name


def test_tolerations_can_be_specified_or_omitted_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_MAPPING
        subject = render_subject(
            helm_runner=helm_runner,
            values={"tolerations": value},
        )
        pod_spec = subject["spec"]["template"]["spec"]
        if should_omit:
            assert "tolerations" not in pod_spec
        else:
            assert pod_spec["tolerations"] == value


def test_persistence_claim_name_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    existing_claim_name = factories.random_string()
    subject = render_subject(
        helm_runner=helm_runner,
        values={"persistence": {"existingClaimName": existing_claim_name}},
    )
    volume = subject["spec"]["template"]["spec"]["volumes"][0]
    assert volume["persistentVolumeClaim"]["claimName"] == existing_claim_name


def test_tz_environment_variable_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    timezone = factories.random_string()
    subject = render_subject(
        helm_runner=helm_runner,
        values={"timezone": timezone},
    )
    container = get_container(subject)
    tz_variable = [
        variable for variable in container["env"] if variable["name"] == "TZ"
    ][0]
    assert tz_variable["value"] == timezone


def test_image_repository_can_be_customized_with_appropriate_value(
    app_version: str,
    helm_runner: HelmRunner,
) -> None:
    image_repository = factories.random_string()
    subject = render_subject(
        helm_runner=helm_runner,
        values={"image": {"repository": image_repository}},
    )
    container = get_container(subject)

    expected_image = f"{image_repository}:{app_version}"
    assert container["image"] == expected_image


def test_image_tag_can_be_customized_with_appropriate_value(
    chart_values: Dict,
    helm_runner: HelmRunner,
) -> None:
    image_tag = factories.random_string()
    subject = render_subject(
        helm_runner=helm_runner,
        values={"image": {"tag": image_tag}},
    )
    container = get_container(subject)

    image_repository = chart_values["image"]["repository"]
    expected_image = f"{image_repository}:{image_tag}"
    assert container["image"] == expected_image


def test_image_pull_policy_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    pull_policy = factories.random_string()
    subject = render_subject(
        helm_runner=helm_runner,
        values={"image": {"pullPolicy": pull_policy}},
    )
    container = get_container(subject)

    assert container["imagePullPolicy"] == pull_policy


def test_vpn_tcp_container_port_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    vpn_tcp_port = 42
    subject = render_subject(
        helm_runner=helm_runner,
        values={"service": {"vpnTcpPort": vpn_tcp_port}},
    )
    container = get_container(subject)
    port = [port for port in container["ports"] if port["name"] == "vpn-tcp"][0]
    assert port["containerPort"] == vpn_tcp_port


def test_vpn_udp_container_port_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    vpn_udp_port = 42
    subject = render_subject(
        helm_runner=helm_runner,
        values={"service": {"vpnUdpPort": vpn_udp_port}},
    )
    container = get_container(subject)
    port = [port for port in container["ports"] if port["name"] == "vpn-udp"][0]
    assert port["containerPort"] == vpn_udp_port


def test_vpn_ui_container_port_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    vpn_ui_port = 42
    subject = render_subject(
        helm_runner=helm_runner,
        values={"service": {"vpnUiPort": vpn_ui_port}},
    )
    container = get_container(subject)
    port = [port for port in container["ports"] if port["name"] == "vpn-ui"][0]
    assert port["containerPort"] == vpn_ui_port


def test_readiness_probe_port_can_be_customized_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    vpn_ui_port = 42
    subject = render_subject(
        helm_runner=helm_runner,
        values={"service": {"vpnUiPort": vpn_ui_port}},
    )
    container = get_container(subject)
    assert container["readinessProbe"]["tcpSocket"]["port"] == vpn_ui_port


def test_resources_can_be_specified_or_omitted_with_appropriate_value(
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_MAPPING
        subject = render_subject(
            helm_runner=helm_runner,
            values={"resources": value},
        )
        container = get_container(subject)
        if should_omit:
            assert "resources" not in container
        else:
            assert container["resources"] == value


def test_security_context_can_be_specified_or_omitted_with_appropriate_value(
    chart_values: Dict,
    helm_runner: HelmRunner,
) -> None:
    for should_omit in [False, True]:
        value = None if should_omit else EXAMPLE_MAPPING
        subject = render_subject(
            helm_runner=helm_runner,
            values={"securityContext": value},
        )
        container = get_container(subject)
        if should_omit:
            assert "securityContext" not in container
        else:
            expected_security_context = chart_values["securityContext"] | value
            assert container["securityContext"] == expected_security_context


def get_container(subject: Dict) -> Dict:
    container = subject["spec"]["template"]["spec"]["containers"][0]
    assert isinstance(container, Dict)
    return container


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
