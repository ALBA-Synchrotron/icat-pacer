from __future__ import absolute_import, unicode_literals


def register_custom_serializers(serializer_register_func: list) -> None:
    for serializer_path in serializer_register_func:
        module_name, function_name = serializer_path.rsplit('.', 1)
        module = __import__(module_name, fromlist=[function_name])
        getattr(module, function_name)()
