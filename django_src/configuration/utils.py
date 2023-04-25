import os


def get_env_bool(key: str, default: bool) -> bool:
    """
    Retrieves a bool from the environment variables.
    """
    env_value = os.environ.get(key, default)
    if env_value == "True":
        return True
    elif env_value == "False":
        return False
    elif env_value == True:
        return True
    elif env_value == False:
        return False
    else:
        raise Exception("Environment bool value cannot be interpreted")


def get_env_str(key: str, default: str) -> str:
    """
    Retrieves a string from the environment variables.
    """
    return os.environ.get(key, default)
