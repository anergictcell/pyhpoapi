import warnings


from fastapi import HTTPException

from pyhpo.ontology import Ontology
from pyhpo.set import HPOSet


def get_hpo_term(termid):

    try:
        identifier = int(termid)
    except ValueError:
        identifier = termid

    term = Ontology.get_hpo_object(identifier)
    if term is None:
        raise HTTPException(
            status_code=404,
            detail='HPO Term does not exist',
            headers={'X-TermNotFound': termid}
        )
    return term


def get_hpo_id(termid):
    warnings.warn("This method is deprecated", DeprecationWarning)
    try:
        return int(termid)
    except ValueError:
        return termid


def get_hpo_set(set_query):
    try:
        return HPOSet([
            get_hpo_term(x)
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
            detail='Invalid query'
        )
