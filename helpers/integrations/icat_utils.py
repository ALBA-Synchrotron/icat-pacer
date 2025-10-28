import re
from typing import Iterable

from icat import Client
from icat.entity import Entity
from icat.query import Query


class ICATClient:
    client: Client
    session_id: str = None

    def __init__(self, url: str, username: str = None, password: str = None, auth_plugin: str = None,
                 session_id: str = None) -> None:
        self.client = Client(url)

        if session_id:
            self.session_id = session_id
            self.client.sessionId = session_id
        elif username and password and auth_plugin:
            self.client.login(
                auth_plugin,
                {"username": username, "password": password}
            )
            if self.client.sessionId:
                self.session_id = self.client.sessionId

    def __del__(self) -> None:
        if self.client and self.client.sessionId:
            self.client.logout()

    def auto_refresh_session(self) -> None:
        self.client.autoRefresh()

    def logout(self) -> None:
        self.client.logout()

    @classmethod
    def open_icat_session(cls, config: dict, session_id: str = None) -> Client | None:
        icat_config: dict = config.get("", {}).get("icat", {})
        enabled: bool = icat_config.get("enabled", False)

        if not icat_config or not enabled:
            return None

        icat_server_config: dict = icat_config.get("server", {})
        url: str = icat_server_config.get("url", "")
        auth_plugin: str = icat_server_config.get("authPlugin", "")
        username: str = icat_server_config.get("username", "")
        password: str = icat_server_config.get("password", "")

        icat_client = cls(url, username, password, auth_plugin, session_id=session_id)
        if session_id:
            icat_client.sessionId = session_id
        return icat_client

    @classmethod
    def __to_sql_in_clause(cls, values: Iterable) -> str:
        formatted = []
        for v in values:
            if isinstance(v, str):
                escaped = v.replace("'", "''")
                formatted.append(f"'{escaped}'")
            elif v is None:
                formatted.append("NULL")
            else:
                formatted.append(str(v))
        return f"{', '.join(formatted)}"

    @classmethod
    def __parse_custom_conditions(cls, conditions: dict) -> dict:
        result = conditions.copy()

        for c in list(conditions.keys()):
            if bool(re.search(r'\b\w+__\w+\b', c)):
                value = result.pop(c)
                try:
                    field, operator = c.split("__")
                except ValueError:
                    raise ValueError(f"Invalid custom condition format: {c}")

                match operator:
                    case "eq":
                        if value is None:
                            result[field] = "IS NULL"
                            continue

                        result[field] = f"= '{value}'"
                    case "in":
                        if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
                            raise ValueError(f"Value must be non-string iterable for IN operator: {value}")
                        result[field] = f"IN ({cls.__to_sql_in_clause(value)})"
                    case "gt":
                        result[field] = f"> {value}"
                    case "gte":
                        result[field] = f">= {value}"
                    case "lt":
                        result[field] = f"< {value}"
                    case "lte":
                        result[field] = f"<= {value}"
                    case "like" | "contains":
                        result[field] = f"LIKE '%{value}%'"
                    case "startswith":
                        result[field] = f"LIKE '{value}%'"
                    case "endswith":
                        result[field] = f"LIKE '%{value}'"
                    case _:
                        raise ValueError(f"Invalid operator '{operator}' for custom condition.")

        return result

    def search(self, entity: str, attributes=None, aggregate=None, order=None,
               conditions=None, includes=None, limit=None,
               join_specs=None, flatten_single=True) -> Entity | list[Entity] | None:
        if conditions:
            conditions = self.__parse_custom_conditions(conditions)

        query: Query = Query(self.client, entity, attributes=attributes, aggregate=aggregate, order=order,
                             conditions=conditions, includes=includes, limit=limit,
                             join_specs=join_specs)

        results: list = self.client.search(query)

        if results:
            return results[0] if len(results) == 1 and flatten_single else results
        return None

    def new(self, *args, **kwargs) -> Entity:
        return self.client.new(*args, **kwargs)

    def delete(self, entity: Entity) -> None:
        self.client.delete(entity)
