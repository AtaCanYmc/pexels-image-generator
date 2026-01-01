import os


def get_env_file_as_kvp_list(env_file_path: str) -> list[dict[str, str]]:
    kvp_list = []
    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f".env file not found at path: {env_file_path}")

    with open(env_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    kvp_list.append({'key': key.strip(), 'value': value.strip()})

    return kvp_list
