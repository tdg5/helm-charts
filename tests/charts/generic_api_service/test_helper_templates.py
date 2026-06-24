from typing import Any, Dict

import yaml

from tests.charts.generic_api_service import (
    CHART_NAME,
    EXAMPLE_APP_NAME,
    EXAMPLE_APP_VERSION,
)
from tests.test_helpers import HelperRenderer, random_string
from tests.test_helpers.test_constants import EXAMPLE_RELEASE_NAME


def test_app_name_comes_from_name_value(helper_renderer: HelperRenderer) -> None:
    expected_app_name = EXAMPLE_APP_NAME
    app_name = helper_renderer.render(
        helper_name="app-name",
        values={"appName": expected_app_name},
    )
    assert app_name == expected_app_name


def test_app_name_truncates_name_to_63_characters(
    helper_renderer: HelperRenderer,
) -> None:
    chars = "abcdefghi"
    given_app_name = chars * 8
    app_name = helper_renderer.render(
        helper_name="app-name",
        values={"appName": given_app_name},
    )
    assert app_name == chars * 7


def test_app_name_removes_dash_suffix(helper_renderer: HelperRenderer) -> None:
    chars = "abcdefghij" * 6
    given_app_name = f"{chars}xx-x"
    assert 64 == len(given_app_name)
    app_name = helper_renderer.render(
        helper_name="app-name",
        values={"appName": given_app_name},
    )
    assert app_name == f"{chars}xx"


def test_app_version_defaults_to_container_image_tag_value(
    helper_renderer: HelperRenderer,
    random_required_values: Dict[str, Any],
) -> None:
    values = random_required_values
    image_tag = random_string()
    values["container"]["image"]["tag"] = image_tag
    app_version = helper_renderer.render(
        "app-version",
        values=values,
    )
    assert app_version == image_tag


def test_app_version_can_be_configured_with_app_version_value(
    helper_renderer: HelperRenderer,
    random_required_values: Dict[str, Any],
) -> None:
    values = random_required_values
    expected_app_version = EXAMPLE_APP_VERSION
    values["appVersion"] = expected_app_version
    app_version = helper_renderer.render(
        "app-version",
        values=values,
    )
    assert app_version == expected_app_version


def test_full_name_default_value(helper_renderer: HelperRenderer) -> None:
    app_name = EXAMPLE_APP_NAME
    release_name = EXAMPLE_RELEASE_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": app_name},
    )
    assert full_name == f"{release_name}-{app_name}"


def test_full_name_uses_release_name_as_the_full_name_if_release_name_includes_chart_name(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    app_name = EXAMPLE_APP_NAME
    release_name = f"release-name-{app_name}"
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": app_name},
    )
    assert full_name == release_name


def test_full_name_uses_release_name_as_the_full_name_if_release_name_includes_name_value(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    app_name = EXAMPLE_APP_NAME
    release_name = f"release-name-{app_name}-xxx"
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": app_name},
    )
    assert full_name == release_name


def test_full_name_combines_release_name_and_chart_name_if_release_name_does_not_include_chart_name(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    app_name = EXAMPLE_APP_NAME
    release_name = EXAMPLE_RELEASE_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": app_name},
    )
    assert full_name == f"{release_name}-{app_name}"


def test_full_name_combines_release_name_and_name_value_if_release_name_does_not_include_name_value(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    app_name = EXAMPLE_APP_NAME
    release_name = EXAMPLE_RELEASE_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": app_name},
    )
    assert full_name == f"{release_name}-{app_name}"


def test_full_name_combined_name_truncates_length_to_63_chars(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    app_name = "x" * (63 - len(release_name) - 1)
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": f"{app_name}123"},
    )
    assert 63 == len(full_name)
    assert full_name == f"{release_name}-{app_name}"


def test_full_name_combined_name_removes_dash_suffix(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    app_name = "x" * (62 - len(release_name) - 1)
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": f"{app_name}-123"},
    )
    assert 62 == len(full_name)
    assert full_name == f"{release_name}-{app_name}"


def test_chart_default_value_combines_chart_name_and_chart_version(
    chart_version: str,
    helper_renderer: HelperRenderer,
) -> None:
    chart = helper_renderer.render("chart")
    assert chart == f"{CHART_NAME}-{chart_version}"


def test_labels_includes_expected_labels(
    chart_version: str,
    helper_renderer: HelperRenderer,
) -> None:
    app_name = EXAMPLE_APP_NAME
    app_version = EXAMPLE_APP_VERSION
    release_name = "release-name"
    labels_yaml = helper_renderer.render(
        helper_name="labels",
        name=release_name,
        values={"appName": app_name, "appVersion": app_version},
    )
    labels = yaml.safe_load(labels_yaml)
    assert len(labels) == 5
    assert labels["app.kubernetes.io/instance"] == release_name
    assert labels["app.kubernetes.io/managed-by"] == "Helm"
    assert labels["app.kubernetes.io/name"] == app_name
    assert labels["app.kubernetes.io/version"] == app_version
    assert labels["helm.sh/chart"] == f"{CHART_NAME}-{chart_version}"


def test_selector_labels_includes_expected_labels(
    helper_renderer: HelperRenderer,
) -> None:
    app_name = EXAMPLE_APP_NAME
    release_name = EXAMPLE_RELEASE_NAME
    selector_labels_yaml = helper_renderer.render(
        helper_name="selector-labels",
        name=release_name,
        values={"appName": app_name},
    )
    selector_labels = yaml.safe_load(selector_labels_yaml)
    assert len(selector_labels) == 2
    assert selector_labels["app.kubernetes.io/instance"] == release_name
    assert selector_labels["app.kubernetes.io/name"] == app_name


def test_service_account_name_is_default_when_will_not_create_and_no_name_set(
    helper_renderer: HelperRenderer,
) -> None:
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        values={"serviceAccount": {"create": False}},
    )
    assert service_account_name == "default"


def test_service_account_name_is_expected_name_when_will_not_create_and_name_set(
    helper_renderer: HelperRenderer,
) -> None:
    app_name = "service-account-name"
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        values={"serviceAccount": {"create": False, "name": app_name}},
    )
    assert service_account_name == app_name


def test_service_account_name_is_expected_default_when_will_create_and_no_name_set(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = "release-name"
    default_name = helper_renderer.render(
        "full-name",
        name=release_name,
    )
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        name=release_name,
        values={"serviceAccount": {"create": True}},
    )
    assert service_account_name == default_name


def test_service_account_name_is_expected_name_when_will_create_and_name_set(
    helper_renderer: HelperRenderer, random_required_values: Dict[str, Any]
) -> None:
    app_name = "service-account-name"
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        values={"serviceAccount": {"create": True, "name": app_name}},
    )
    assert service_account_name == app_name


def test_service_name_defaults_to_full_name_template(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    app_name = EXAMPLE_APP_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": app_name},
    )
    service_name = helper_renderer.render(
        helper_name="service-name",
        name=release_name,
        values={"appName": app_name},
    )
    assert service_name == full_name


def test_service_name_can_be_configured_with_service_name_value(
    helper_renderer: HelperRenderer,
    random_required_values: Dict[str, Any],
) -> None:
    values = random_required_values
    expected_service_name = random_string()
    values["service"] = {"name": expected_service_name}
    service_name = helper_renderer.render(helper_name="service-name", values=values)
    assert service_name == expected_service_name


def test_namespace_name_defaults_to_full_name_template(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    app_name = EXAMPLE_APP_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"appName": app_name},
    )
    namespace_name = helper_renderer.render(
        helper_name="namespace-name",
        name=release_name,
        values={"appName": app_name},
    )
    assert namespace_name == full_name


def test_namespace_name_can_be_configured_with_namespace_name_value(
    helper_renderer: HelperRenderer,
    random_required_values: Dict[str, Any],
) -> None:
    values = random_required_values
    expected_namespace_name = random_string()
    values["namespace"] = {"name": expected_namespace_name}
    namespace_name = helper_renderer.render(
        helper_name="namespace-name",
        values=values,
    )
    assert namespace_name == expected_namespace_name


def test_http_route_api_version_defaults_to_gateway_v1(
    helper_renderer: HelperRenderer,
) -> None:
    api_version = helper_renderer.render(helper_name="http-route-api-version")
    assert api_version == "gateway.networking.k8s.io/v1"


def test_http_route_api_version_can_be_set_with_global_gateway_api_value(
    helper_renderer: HelperRenderer,
) -> None:
    expected_api_version = "gateway.networking.k8s.io/v1beta1"
    api_version = helper_renderer.render(
        helper_name="http-route-api-version",
        values={"global": {"gatewayApi": {"apiVersion": expected_api_version}}},
    )
    assert api_version == expected_api_version


def test_backend_tls_policy_api_version_defaults_to_v1alpha3(
    helper_renderer: HelperRenderer,
) -> None:
    api_version = helper_renderer.render(
        helper_name="backend-tls-policy-api-version",
    )
    assert api_version == "gateway.networking.k8s.io/v1alpha3"


def test_backend_tls_policy_api_version_can_be_set_with_global_gateway_api_value(
    helper_renderer: HelperRenderer,
) -> None:
    expected_api_version = "gateway.networking.k8s.io/v1"
    api_version = helper_renderer.render(
        helper_name="backend-tls-policy-api-version",
        values={
            "global": {
                "gatewayApi": {"backendTlsPolicyApiVersion": expected_api_version},
            },
        },
    )
    assert api_version == expected_api_version


def test_backend_traffic_policy_api_version_defaults_to_envoy_v1alpha1(
    helper_renderer: HelperRenderer,
) -> None:
    api_version = helper_renderer.render(
        helper_name="backend-traffic-policy-api-version",
    )
    assert api_version == "gateway.envoyproxy.io/v1alpha1"


def test_backend_traffic_policy_api_version_can_be_set_with_global_gateway_api_value(
    helper_renderer: HelperRenderer,
) -> None:
    expected_api_version = "gateway.envoyproxy.io/v1alpha2"
    api_version = helper_renderer.render(
        helper_name="backend-traffic-policy-api-version",
        values={
            "global": {
                "gatewayApi": {"backendTrafficPolicyApiVersion": expected_api_version},
            },
        },
    )
    assert api_version == expected_api_version
