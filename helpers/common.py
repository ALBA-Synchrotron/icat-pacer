from helpers.dataclasses import Affiliation


def get_affiliation_name(affiliation: Affiliation, limit: int = -1) -> str:
    ret: str = f"{', '.join(i for i in [affiliation.name, affiliation.unit, affiliation.department_name] if i != '')}"
    if limit > 0:
        ret = ret[:limit]
    return ret
