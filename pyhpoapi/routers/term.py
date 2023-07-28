from fastapi import APIRouter, Path
from typing import List, Dict

from pyhpo import HPOSet
from pyhpoapi.helpers import get_hpo_term
from pyhpoapi import models

router = APIRouter()


@router.get(
    '/{term_id}',
    response_description='One HPO term',
    response_model=models.HpoTerm
)
async def HPO_term(
        term_id: str = Path(..., example='HP:0000822'),
        verbose: bool = False
) -> dict:
    """
    Show info about a single HPO term.

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    term_id: int or str
        The HPO Term ID
    verbose: bool, default False
        Show more info about the HPOTerm

    Returns
    -------
    dict
        HPOTerm as JSON object

    """
    term = get_hpo_term(term_id).toJSON(bool(verbose))
    res = models.HpoTerm(**term)
    return res.model_dump()


@router.get(
    '/{term_id}/parents',
    response_description='List of HPO terms',
    response_model=List[models.HpoTerm]
)
async def parent_terms(
    term_id: str = Path(..., example='HP:0000822'),
    verbose: bool = False
) -> List[dict]:
    """
    Get all parents of an HPOterm

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    term_id: int or str
        The HPO Term ID
    verbose: bool, default False
        Show more info about the HPOTerm

    Returns
    -------
    dict
        Array of HPOTerms

    """
    return [
        t.toJSON(verbose)
        for t in get_hpo_term(term_id).parents
        ]


@router.get(
    '/{term_id}/children',
    response_description='List of HPO terms',
    response_model=List[models.HpoTerm]

)
async def child_terms(
    term_id: str = Path(..., example='HP:0000822'),
    verbose: bool = False
) -> List[dict]:
    """
    Get all children of an HPOterm

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    term_id: int or str
        The HPO Term ID
    verbose: bool, default False
        Show more info about the HPOTerm

    Returns
    -------
    dict
        Array of HPOTerms

    """
    return [
        t.toJSON(verbose)
        for t in get_hpo_term(term_id).children
        ]


@router.get(
    '/{term_id}/neighbours',
    response_description='The neighouring HPO terms',
    response_model=models.HpoNeighborTerms
)
async def neighbour_terms(
    term_id: str = Path(..., example='HP:0000822'),
    verbose: bool = False
) -> Dict[str, List[dict]]:
    """
    Get all surrounding terms of an HPOterm

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    term_id: int or str
        The HPO Term ID
    verbose: bool, default False
        Show more info about the HPOTerm

    Returns
    -------
    dict
        Dict with the following keys:

        * **parents**: Array of parent HPOTerms
        * **children**: Array of child HPOTerms
        * **neighbours**: Array of 'sibling' HPOTerms

    """
    term = get_hpo_term(term_id)
    parents = HPOSet(list(term.parents))
    children = HPOSet(list(term.children))
    neighbours = HPOSet([])
    for parent in parents:
        for t in parent.children:
            if t != term and t not in parents and t not in children:
                neighbours.add(t)

    for child in children:
        for t in child.parents:
            if t != term and t not in parents and t not in children:
                neighbours.add(t)

    res = {
        'parents': [t.toJSON(verbose) for t in parents],
        'children': [t.toJSON(verbose) for t in children],
        'neighbours': [t.toJSON(verbose) for t in neighbours]
    }
    return res


@router.get(
    '/{term_id}/genes',
    tags=['annotations'],
    response_description='List of Genes',
    response_model=List[models.Gene]

)
async def term_associated_genes(
    term_id: str = Path(..., example='HP:0000822')
) -> List[dict]:
    """
    Get all Genes, associated with an HPOTerm

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    term_id: int or str
        The HPO Term ID

    Returns
    -------
    array
        Array of Genes
    """
    return [
        g.toJSON()
        for g in get_hpo_term(term_id).genes
    ]


@router.get(
    '/{term_id}/omim',
    tags=['annotations'],
    response_description='List of OMIM Diseases',
    response_model=List[models.Omim]
)
async def term_associated_OMIM_diseases(
    term_id: str = Path(..., example='HP:0000822')
) -> List[dict]:
    """
    Get OMIM Diseases, associated with all provided HPOTerms

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    term_id: int or str
        The HPO Term ID

    Returns
    -------
    array
        Array of OMIM diseases
    """
    return [
        d.toJSON()
        for d in get_hpo_term(term_id).omim_diseases
    ]
