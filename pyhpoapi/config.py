import os
import configparser


def config_item_list(value, convert=str):
    return [convert(x) for x in value.split(',')]


local_config = os.path.join(
    os.getcwd(),
    'config.ini'
    )


config = configparser.ConfigParser()
if os.path.exists(local_config):
    config.read(local_config)


VERSION = config.get('default', 'version', fallback='1.0.0')

CORS_ORIGINS = config_item_list(
    config.get('default', 'cors-origins', fallback='')
)
CORS_METHODS = config_item_list(
    config.get('default', 'cors-methods', fallback='')
)
CORS_HEADERS = config_item_list(
    config.get('default', 'cors-headers', fallback='')
)
