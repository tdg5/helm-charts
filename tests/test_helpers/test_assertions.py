import re
from re import Pattern
from typing import Any, Dict, List, Set, Tuple, Union


def assert_dependency_value_override(
    dependency_computed_values: Dict,
    dependency_default_values: Dict,
    expected_default_value: Any,
    expected_override_value: Any,
    path: List[Union[int, str]],
) -> None:
    # First, check the expected default value is there to help detect if a config moves
    target = dependency_default_values
    for path_component in path:
        target = target[path_component]
    assert target == expected_default_value

    # Now it's safe to check the expected override value
    target = dependency_computed_values
    for path_component in path:
        target = target[path_component]
    assert target == expected_override_value


def assert_values_are_known_to_schemas(
    chart_values: Dict,
    chart_values_schema: Dict,
) -> None:
    chart_values_paths = _get_nested_paths(chart_values)
    chart_values_schema_paths = _get_values_schema_paths(chart_values_schema)

    values_without_schema = []
    for chart_value_path_components in chart_values_paths:
        if not _path_matches_any_schema(
            chart_value_path_components,
            chart_values_schema_paths,
        ):
            values_without_schema.append("/".join(chart_value_path_components))

    assert (
        [] == values_without_schema
    ), "Expected all values to have defined schema definitions."


def assert_schemas_are_known_to_values(
    chart_values: Dict,
    chart_values_schema: Dict,
) -> None:
    chart_values_paths = _get_nested_paths(chart_values)
    chart_values_schema_paths = _get_values_schema_paths(chart_values_schema)

    schemas_without_values = []
    for chart_values_schema_path_patterns in chart_values_schema_paths:
        found_match = False
        for chart_value_path_components in chart_values_paths:
            if _path_matches_schema(
                chart_value_path_components,
                chart_values_schema_path_patterns,
            ):
                found_match = True
                break

        if not found_match:
            schemas_without_values.append(
                "/".join([regex.pattern for regex in chart_values_schema_path_patterns])
            )

    assert (
        [] == schemas_without_values
    ), "Expected all schemas to have entries in values.yaml"


def _path_matches_any_schema(
    chart_value_path_components: Tuple[str, ...],
    chart_values_schema_paths: Set[Tuple[Pattern[str], ...]],
) -> bool:
    return any(
        _path_matches_schema(chart_value_path_components, schema_path_patterns)
        for schema_path_patterns in chart_values_schema_paths
    )


def _path_matches_schema(
    chart_value_path_components: Tuple[str, ...],
    chart_values_schema_path_patterns: Tuple[Pattern[str], ...],
) -> bool:
    if len(chart_value_path_components) != len(chart_values_schema_path_patterns):
        return False

    return all(
        path_pattern.fullmatch(path_component)
        for path_component, path_pattern in zip(
            chart_value_path_components,
            chart_values_schema_path_patterns,
        )
    )


def _get_values_schema_paths(
    nested_dict: Dict,
    current_path: Tuple[Pattern[str], ...] = (),
    keys_are_patterns: bool = False,
) -> Set[Tuple[Pattern[str], ...]]:
    """
    Warning: There is no handling for arrays at this time.
    """
    paths: Set[Tuple[Pattern[str], ...]] = set()
    # Skip the first layer of the schema and jump straight to properties
    _nested_dict = nested_dict if len(current_path) > 0 else nested_dict["properties"]

    for key, value in _nested_dict.items():
        key_pattern = key if keys_are_patterns else f"^{re.escape(key)}$"
        new_path = current_path + (re.compile(key_pattern),)
        if value["type"] == "object" and (
            "properties" in value or "patternProperties" in value
        ):
            if "properties" in value:
                paths.update(
                    _get_values_schema_paths(
                        nested_dict=value["properties"],
                        current_path=new_path,
                        keys_are_patterns=False,
                    )
                )
            if "patternProperties" in value:
                paths.update(
                    _get_values_schema_paths(
                        nested_dict=value["patternProperties"],
                        current_path=new_path,
                        keys_are_patterns=True,
                    )
                )
        else:
            paths.add(new_path)

    return paths


def _get_nested_paths(
    nested_dict: Dict,
    current_path: Tuple[str, ...] = (),
) -> Set[Tuple[str, ...]]:
    paths: Set[Tuple[str, ...]] = set()
    for key, value in nested_dict.items():
        new_path = current_path + (key,)
        if value and isinstance(value, dict):
            paths.update(_get_nested_paths(value, new_path))
        else:
            paths.add(new_path)
    return paths
