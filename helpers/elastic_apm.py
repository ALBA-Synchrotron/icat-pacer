import elasticapm


def register_elastic_apm_transaction(transaction_name: str):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if self.apm_client is not None:
                from time import time
                start_time = time()
                elasticapm.instrument()
                self.apm_client.begin_transaction(transaction_name)
                try:
                    result = func(self, *args, **kwargs)
                    duration = time() - start_time
                    self.apm_client.end_transaction(transaction_name, "success", duration=duration)
                    return result
                except Exception as e:
                    duration = time() - start_time
                    self.apm_client.capture_exception()
                    self.apm_client.end_transaction(transaction_name, "error", duration=duration)
                    raise
            else:
                return func(self, *args, **kwargs)
        return wrapper

    return decorator
