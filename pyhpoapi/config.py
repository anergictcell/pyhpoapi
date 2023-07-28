"""
Module to read in a local ``config.ini`` file and store
as a global configuration.
"""

import os
from typing import Any, List


def config_item_list(value: str, convert=str) -> List[Any]:
    """
    Convert a comma separated string into a list
    """
    return [convert(x) for x in value.split(',')]


VERSION = "2.0.0"

MASTER_DATA = os.environ.get("PYHPOAPI_DATA_DIR", "")

CORS_ORIGINS = config_item_list(
    os.environ.get("PYHPOAPI_CORS_ORIGINS", "")
)

CORS_METHODS = config_item_list(
    os.environ.get("PYHPOAPI_CORS_METHODS", "")
)

CORS_HEADERS = config_item_list(
    os.environ.get("PYHPOAPI_CORS_HEADERS", "")
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
