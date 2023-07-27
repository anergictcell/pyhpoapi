"""
Helper functions to convert REST-API GET/POST query parameters to PyHPO objects
"""
from typing import Union

from fastapi import HTTPException

from pyhpo import HPOTerm
from pyhpo import Ontology
from pyhpo import HPOSet


class MockHPOEnrichment:
    def __init__(self, *args, **kwargs):
        pass

    def enrichment(self, *args, **kwargs):
        raise NotImplemented

def get_hpo_term(termid: Union[int, str]) -> HPOTerm:
    """
    Convert the HPO-ID from a REST-API query parameter to an HPOTerm object

    Parameters
    ----------
    termid: str or int
        The HPO-id passed to the REST API

    Returns
    -------
    HPOTerm
    """

    try:
        identifier = int(termid)
    except ValueError:
        identifier = termid  # type: ignore

    try:
        return Ontology.get_hpo_object(identifier)
    except RuntimeError:
        raise HTTPException(
            status_code=404,
            detail='HPO Term does not exist',
            headers={'X-TermNotFound': f"{termid}"}
        )
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail='Invalid HPO identifier',
            headers={'X-TermNotFound': f"{termid}"}
        )


def get_hpo_set(set_query: str) -> HPOSet:
    """
    Build an HPOSet from a set of HPO-IDs passed as parameter to REST API

    Parameters
    ----------
    set_query: str
        Comma separated list of HPO term identifiers

    Returns
    -------
    HPOSet

    Raises
    ------
    HTTPException
        All exceptions fall back to HTTPException and will include an error
        message in the header (either ``X-TermNotFound`` or ``X-Error``)    .
    """
    try:
        return HPOSet([
            get_hpo_term(x.strip())
            for x in set_query.split(',')
        ])
    except HTTPException as ex:
        raise HTTPException(
            status_code=400,
            detail='Invalid HPO Term identifier in query',
            headers=ex.headers
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail='Invalid query',
            headers={'X-Error': 'Invalid query provided'}
        )
