import os


def require_env(env_name):
    env_value = os.environ.get(env_name)
    if not env_value:
        raise Exception("$%s is not set" % env_name)
    return env_value
