from typing import Any, Dict, Optional
from uuid import uuid4

from pytest_helm_templates import HelmRunner


class HelperRenderer:
    def __init__(
        self,
        chart_name: str,
        helm_runner: HelmRunner,
    ) -> None:
        self._chart_name: str = chart_name
        self._helm_runner: HelmRunner = helm_runner

    def render(
        self,
        helper_name: str,
        name: str = "",
        helper_namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
    ) -> str:
        _helper_namespace = helper_namespace or self._chart_name
        _helper_name = f"{_helper_namespace}.{helper_name}"
        helper_template = (
            f"""---\nresult: |-\n  {{{{- include "{_helper_name}" . | nindent 2}}}}"""
        )
        rendered_helper = self._helm_runner.adhoc_template(
            chart=self._chart_name,
            content=helper_template,
            name=name or str(uuid4()),
            values=[values] if values else [],
        )
        helper_result = rendered_helper["result"]
        assert isinstance(helper_result, str)
        return helper_result
