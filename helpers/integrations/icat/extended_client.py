import re
from typing import Iterable, TypeVar

import suds
from icat import Client, translateError
from icat.entity import Entity
from icat.query import Query

T = TypeVar("T")


class ICATClient(Client):
    def __init__(self, url: str, username: str = None, password: str = None, auth_plugin: str = None,
                 session_id: str = None, *_args, **_kwargs) -> None:

        super().__init__(url=url)

        if session_id:
            self.sessionId = session_id
        elif username and password and auth_plugin:
            self.login(
                auth_plugin,
                {"username": username, "password": password}
            )
        self.__replace_entity_getattr_method()
        self.__add_entity_count_method()

    def __del__(self) -> None:
        super().__del__()
        self.logout()

    def auto_refresh_session(self) -> None:
        self.autoRefresh()

    @classmethod
    def __add_entity_count_method(cls):

        def count(self, name: str) -> int:
            if name not in self.InstMRel:
                raise ValueError(f"Entity {self.BeanName} has no many-to-many relation named {name}")

            return self.client.search(self.BeanName, attributes=[f"{name}"], aggregate="COUNT",
                                      conditions={"id__eq": self.id})

        Entity.count = count

    @classmethod
    def __replace_entity_getattr_method(cls):
        old_getattr = Entity.__getattr__

        def new_get_attr_func(self, name, lazy_loaded: bool = False) -> T:
            res = old_getattr(self, name)

            if callable(res):
                return res

            if not res and name in [*self.InstRel, *self.InstMRel] and not lazy_loaded:
                updated_entity = self.client.query_search(
                    f"SELECT b FROM {self.BeanName} b WHERE b.id = {self.id} INCLUDE b.{name}")
                loaded_value = updated_entity.__getattr__(name, lazy_loaded=True)
                setattr(self, name, loaded_value)
                return loaded_value
            return res

        Entity.__getattr__ = new_get_attr_func

    @classmethod
    def open_icat_session(cls, config: dict, session_id: str = None) -> Client | None:
        icat_config: dict = config.get("integrations", {}).get("icat", {})
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
                        if isinstance(value, str):
                            result[field] = f"> '{value}'"
                        else:
                            result[field] = f"> {value}"
                    case "gte":
                        if isinstance(value, str):
                            result[field] = f">= '{value}'"
                        else:
                            result[field] = f">= {value}"
                    case "lt":
                        if isinstance(value, str):
                            result[field] = f"< '{value}'"
                        else:
                            result[field] = f"< {value}"
                    case "lte":
                        if isinstance(value, str):
                            result[field] = f"<= '{value}'"
                        else:
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
        results: list
        if conditions:
            conditions = self.__parse_custom_conditions(conditions)

        query: Query = Query(self, entity, attributes=attributes, aggregate=aggregate, order=order,
                             conditions=conditions, includes=includes, limit=limit,
                             join_specs=join_specs)

        try:
            instances = self.service.search(self.sessionId, str(query))
            results = [self.getEntity(i) for i in instances]
        except suds.WebFault as e:
            raise translateError(e)

        if results:
            return results[0] if len(results) == 1 and flatten_single else results
        return None

    def query_search(self, query: str | Query, flatten_single: bool = True) -> list:
        results = super().search(query)
        return results[0] if len(results) == 1 and flatten_single else results
