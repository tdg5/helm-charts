import yaml

from tests.charts.openvpn_as import CHART_NAME
from tests.test_helpers import HelperRenderer
from tests.test_helpers.test_constants import EXAMPLE_RELEASE_NAME


def test_name_comes_from_chart_name_by_default(helper_renderer: HelperRenderer) -> None:
    expected_name = CHART_NAME
    name = helper_renderer.render(helper_name="name")
    assert name == expected_name


def test_name_can_be_customized_with_name_override_value(
    helper_renderer: HelperRenderer,
) -> None:
    expected_name = "name-override"
    name = helper_renderer.render(
        helper_name="name",
        values={"nameOverride": expected_name},
    )
    assert name == expected_name


def test_name_truncates_result_to_63_characters(
    helper_renderer: HelperRenderer,
) -> None:
    chars = "abcdefghi"
    expected_name = chars * 7
    name_override = expected_name + chars
    name = helper_renderer.render(
        helper_name="name",
        values={"nameOverride": name_override},
    )
    assert name == expected_name


def test_name_removes_leftover_dash(helper_renderer: HelperRenderer) -> None:
    expected_name = f'{"abcdefghij" * 6}ab'
    name_override = f"{expected_name}-c"
    assert 64 == len(name_override)
    name = helper_renderer.render(
        helper_name="name",
        values={"nameOverride": name_override},
    )
    assert name == expected_name


def test_full_name_comes_from_release_name_and_chart_name_by_default(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
    )
    assert full_name == f"{release_name}-{CHART_NAME}"


def test_full_name_uses_name_override_instead_of_chart_name_when_given_name_override(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    name_override = "name-override"
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"nameOverride": name_override},
    )
    assert full_name == f"{release_name}-{name_override}"


def test_full_name_is_release_name_if_the_release_name_includes_the_chart_name(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = f"{EXAMPLE_RELEASE_NAME}-{CHART_NAME}"
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
    )
    assert full_name == release_name


def test_full_name_is_release_name_if_the_release_name_includes_the_name_override_value(
    helper_renderer: HelperRenderer,
) -> None:
    name_override = "name-override"
    release_name = f"{EXAMPLE_RELEASE_NAME}-{name_override}"
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"nameOverride": name_override},
    )
    assert full_name == release_name


def test_full_name_is_release_name_and_chart_name_when_chart_name_not_in_release_name(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
    )
    assert full_name == f"{release_name}-{CHART_NAME}"


def test_full_name_is_release_name_and_name_override_if_chart_name_not_in_name_override(
    helper_renderer: HelperRenderer,
) -> None:
    name_override = "name-override"
    release_name = EXAMPLE_RELEASE_NAME
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"nameOverride": name_override},
    )
    assert full_name == f"{release_name}-{name_override}"


def test_full_name_truncates_length_to_63_characters_when_given_name_override(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    truncated_name_override = "a" * (62 - len(release_name))
    name_override = f"{truncated_name_override}abc"
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"nameOverride": name_override},
    )
    assert 63 == len(full_name)
    assert full_name == f"{release_name}-{truncated_name_override}"


def test_full_name_removes_trailing_dash_when_given_name_override(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    truncated_name_override = "a" * (61 - len(release_name))
    name_override = f"{truncated_name_override}-abc"
    full_name = helper_renderer.render(
        helper_name="full-name",
        name=release_name,
        values={"nameOverride": name_override},
    )
    assert 62 == len(full_name)
    assert full_name == f"{release_name}-{truncated_name_override}"


def test_full_name_truncates_length_to_63_characters_when_given_full_name_override(
    helper_renderer: HelperRenderer,
) -> None:
    truncated_full_name_override = "a" * 63
    full_name_override = f"{truncated_full_name_override}abc"
    full_name = helper_renderer.render(
        helper_name="full-name",
        values={"fullNameOverride": full_name_override},
    )
    assert 63 == len(full_name)
    assert full_name == truncated_full_name_override


def test_full_name_removes_trailing_dash_when_given_full_name_override(
    helper_renderer: HelperRenderer,
) -> None:
    truncated_full_name_override = "a" * 62
    full_name_override = f"{truncated_full_name_override}-abc"
    full_name = helper_renderer.render(
        helper_name="full-name",
        values={"fullNameOverride": full_name_override},
    )
    assert full_name == truncated_full_name_override


def test_chart_default_value_combines_chart_name_and_chart_version(
    chart_version: str,
    helper_renderer: HelperRenderer,
) -> None:
    chart = helper_renderer.render("chart")
    assert chart == f"{CHART_NAME}-{chart_version}"


def test_labels_includes_expected_default_labels(
    app_version: str,
    chart_version: str,
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    labels_yaml = helper_renderer.render(
        helper_name="labels",
        name=release_name,
    )
    chart_helper_result = helper_renderer.render("chart")
    name_helper_result = helper_renderer.render("name", name=release_name)
    labels = yaml.safe_load(labels_yaml)
    assert len(labels) == 5
    assert labels["app.kubernetes.io/instance"] == release_name
    assert labels["app.kubernetes.io/managed-by"] == "Helm"
    assert labels["app.kubernetes.io/name"] == name_helper_result
    assert labels["app.kubernetes.io/version"] == app_version
    assert labels["helm.sh/chart"] == chart_helper_result


def test_selector_labels_includes_expected_labels(
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    selector_labels_yaml = helper_renderer.render(
        helper_name="selector-labels",
        name=release_name,
    )
    name_helper_result = helper_renderer.render("name")
    selector_labels = yaml.safe_load(selector_labels_yaml)
    assert len(selector_labels) == 2
    assert selector_labels["app.kubernetes.io/instance"] == release_name
    assert selector_labels["app.kubernetes.io/name"] == name_helper_result


def test_service_account_name_is_default_no_name_given_and_service_account_will_not_be_created(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        values={"serviceAccount": {"create": False}},
    )
    assert service_account_name == "default"


def test_service_account_name_is_expected_name_when_will_not_create_and_service_account_name_given(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    expected_service_account_name = "service-account-name"
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        values={
            "serviceAccount": {"create": False, "name": expected_service_account_name}
        },
    )
    assert service_account_name == expected_service_account_name


def test_service_account_name_is_full_name_when_service_account_will_be_created_and_no_name_set(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    release_name = EXAMPLE_RELEASE_NAME
    full_name_helper_result = helper_renderer.render("full-name", name=release_name)
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        name=release_name,
        values={"serviceAccount": {"create": True}},
    )
    assert service_account_name == full_name_helper_result


def test_service_account_name_is_expected_name_when_service_account_will_be_created_and_name_set(  # noqa: E501
    helper_renderer: HelperRenderer,
) -> None:
    expected_service_account_name = "service-account-name"
    service_account_name = helper_renderer.render(
        helper_name="service-account-name",
        values={
            "serviceAccount": {
                "create": True,
                "name": expected_service_account_name,
            },
        },
    )
    assert service_account_name == expected_service_account_name
