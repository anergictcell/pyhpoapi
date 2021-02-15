"""
Module to read in a local ``config.ini`` file and store
as a global configuration.
"""

import os
import configparser
from typing import Any, List


def config_item_list(value: str, convert=str) -> List[Any]:
    """
    Convert a comma separated string into a list
    """
    return [convert(x) for x in value.split(',')]


local_config = os.path.join(
    os.getcwd(),
    'config.ini'
    )


config = configparser.ConfigParser()
if os.path.exists(local_config):
    config.read(local_config)


VERSION = config.get('default', 'version', fallback='1.2.1')

CORS_ORIGINS = config_item_list(
    config.get('default', 'cors-origins', fallback='')
)
CORS_METHODS = config_item_list(
    config.get('default', 'cors-methods', fallback='')
)
CORS_HEADERS = config_item_list(
    config.get('default', 'cors-headers', fallback='')
)

OPENAPI_TAGS = [
    {
        'name': 'term',
        'description': 'Operate on a single HPOTerm',
    },
    {
        'name': 'terms',
        'description': 'Operate on one or multiple HPOSets',
    },
    {
        'name': 'annotations',
        'description': (
            'Operate on the Gene and Disease associations of '
            'HPOTerms or HPOSets'
        )
    },
    {
        'name': 'gene',
        'description': (
            'Operate on genes and their association to '
            'HPOTerms or HPOSets'
        )
    },
    {
        'name': 'disease',
        'description': (
            'Operate on diseases and their association to '
            'HPOTerms or HPOSets'
        )
    },
    {
        'name': 'similarity',
        'description': (
            'Commpare HPOTerms and HPOSets with each other, '
            'with genes or diseases and calculate similarity scores'
        ),
    },
    {
        'name': 'enrichment',
        'description': (
            'Calculate enrichment scores of HPOTerms, Genes or Diseases'
        ),
    }
]
