from typing import Dict

from tests.test_helpers.test_assertions import (
    assert_schemas_are_known_to_values,
    assert_values_are_known_to_schemas,
)


def test_values_are_known_to_schemas(
    chart_values: Dict,
    chart_values_schema: Dict,
) -> None:
    assert_values_are_known_to_schemas(
        chart_values=chart_values,
        chart_values_schema=chart_values_schema,
    )


def test_schemas_are_known_to_values(
    chart_values: Dict,
    chart_values_schema: Dict,
) -> None:
    assert_schemas_are_known_to_values(
        chart_values=chart_values,
        chart_values_schema=chart_values_schema,
    )
