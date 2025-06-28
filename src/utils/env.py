import os
import sys
from dotenv import load_dotenv, set_key, unset_key


class Env:

    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

    def __str__(self):
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith('_')}
        return str(env_vars)

    def __getattr__(self, attr):
        value = os.environ.get(attr)
        if value is None:
            ex = AttributeError(f"Attribute {attr} not found in environment variables")
            return None
        return value

    def __setattr__(self, attr, value):
        if not isinstance(value, str):
            ex = TypeError(f"Cannot set non-string value as environment variable: {attr}")
            raise ex
        os.environ[attr] = value
        set_key('.env', attr, value)

    def __delattr__(self, attr):
        if attr in os.environ:
            unset_key('.env', attr)
            del os.environ[attr]
        else:
            ex = AttributeError(f"Attribute {attr} not found in environment variables")
            raise ex


env = Env()


if __name__ == '__main__':
    print(env)
