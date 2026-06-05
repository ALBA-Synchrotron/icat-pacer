import json

from helpers.models.investigation import InvestigationOperationsContext


def create_investigation_ops_context(inv_ops_data: str | dict) -> InvestigationOperationsContext:
    inv_ops_dict: dict = json.loads(inv_ops_data) if isinstance(inv_ops_data, str) else inv_ops_data
    return InvestigationOperationsContext(
        name=inv_ops_dict.get("name", ""),
        operations=inv_ops_dict.get("operations", []),
        visit_id=inv_ops_dict.get("visit_id", "")
    )
