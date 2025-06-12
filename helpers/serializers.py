from __future__ import absolute_import, unicode_literals

from conf.definitions import CUSTOM_SERIALIZER_REGISTER_FUNCTIONS


def register_custom_serializers() -> None:
    for serializer_path in CUSTOM_SERIALIZER_REGISTER_FUNCTIONS:
        module_name, function_name = serializer_path.rsplit('.', 1)
        module = __import__(module_name, fromlist=[function_name])
        getattr(module, function_name)()
