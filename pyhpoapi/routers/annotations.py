from fastapi import APIRouter, HTTPException, Path, Query

from pyhpo.ontology import Ontology
from pyhpo.annotations import Gene, Omim
from pyhpo.set import HPOSet

from pyhpoapi.helpers import get_hpo_set
from pyhpoapi import models
from pyhpoapi.routers import terms

router = APIRouter()


@router.get(
    '/omim/{omim_id}',
    tags=['disease'],
    response_description='OMIM Disease',
    response_model=models.Omim

)
async def omim_disease(
    omim_id: int = Path(..., example=230800),
    verbose: bool = False
):
    """
    Show info about an OMIM diseae

    Parameters
    ----------
    omim_id: int
        The OMIM ID
    verbose: bool, default False
        Show associated HPO term IDs

    Returns
    -------
    array
        OMIM Disease

    """
    try:
        res = Omim.get(omim_id).toJSON(verbose=verbose)
    except KeyError:
        raise HTTPException(status_code=404, detail='OMIM disease does not exist')
    try:
        res['hpo'] = [Ontology[x].toJSON() for x in res['hpo']]
    except KeyError:
        pass
    return res


@router.get(
    '/gene/{gene_id}',
    tags=['gene'],
    response_description='Gene',
    response_model=models.Gene
)
async def gene(
    gene_id=Path(..., example='GBA'),
    verbose: bool = False
):
    """
    Show info about an OMIM diseae

    Parameters
    ----------
    omim_id: int or str
        The HGNC gene-id or gene-symbol
    verbose: bool, default False
        Show associated HPO term IDs

    Returns
    -------
    array
        Gene

    """
    try:
        res = Gene.get(gene_id).toJSON(verbose=verbose)
    except KeyError:
        raise HTTPException(status_code=404, detail="Gene does not exist")
    try:
        res['hpo'] = [Ontology[x].toJSON() for x in res['hpo']]
    except KeyError:
        pass
    return res


@router.get(
    '/similarity/omim',
    tags=['similarity', 'terms', 'disease'],
    response_description='Similarity score',
    response_model=models.Similarity_Score_OMIM
    )
async def omim_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    omim: int = Query(..., example=230800),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
):
    """
    Similarity score between one HPOSet and an OMIM Disease
    """
    set1 = get_hpo_set(set1)
    try:
        disease = Omim.get(omim)
    except KeyError:
        raise HTTPException(status_code=404, detail="OMIM disease does not exist")
    set2 = HPOSet.from_queries(disease.hpo)

    return {
        'set1': set1.toJSON(),
        'set2': set2.toJSON(),
        'omim': disease.toJSON(),
        'similarity': set1.similarity(
            set2,
            kind=kind,
            method=method,
            combine=combine
        )
    }


@router.post(
    '/similarity/omim',
    tags=['similarity', 'terms', 'disease'],
    response_description='Similarity score',
    response_model=models.Batch_Similarity_Score
    )
async def batch_omim_similarity(
    data: models.POST_OMIM_Batch,
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
):
    """
    Similarity score between one HPOSet and several OMIM Diseases
    """
    other_sets = []

    for other in data.omim_diseases:
        try:
            disease = Omim.get(other)
            hpos = ','.join([str(x) for x in disease.hpo])
        except KeyError:
            hpos = ''

        other_sets.append(
            models.POST_HPOSet(
                set2=hpos,
                name=other
            )
        )

    res = await terms.batch_similarity(
        data=models.POST_Batch(
            set1=data.set1,
            other_sets=other_sets
            ),
        method=method,
        combine=combine,
        kind=kind
    )
    return res


@router.get(
    '/similarity/omim/all',
    tags=['similarity', 'terms', 'disease'],
    response_description='Similarity score',
    response_model=models.Batch_Similarity_Score
    )
async def all_omim_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
):
    """
    Calculate Similarity scores between query set and all OMIM diseases
    """

    data = models.POST_OMIM_Batch(
        set1=set1,
        omim_diseases=[x.id for x in Ontology.omim_diseases]
    )
    res = await batch_omim_similarity(
        data=data,
        method=method,
        combine=combine,
        kind=kind
    )
    return res


@router.get(
    '/similarity/gene',
    tags=['similarity', 'terms', 'disease'],
    response_description='Similarity score',
    response_model=models.Similarity_Score_Gene
    )
async def gene_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    gene: str = Query(..., example='GBA'),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
):
    """
    Similarity score between one HPOSet and an OMIM Disease
    """
    set1 = get_hpo_set(set1)
    try:
        actual_gene = Gene.get(gene)
    except KeyError:
        raise HTTPException(status_code=404, detail="Gene does not exist")
    set2 = HPOSet.from_queries(actual_gene.hpo)

    return {
        'set1': set1.toJSON(),
        'set2': set2.toJSON(),
        'gene': actual_gene.toJSON(),
        'similarity': set1.similarity(
            set2,
            kind=kind,
            method=method,
            combine=combine
        )
    }


@router.post(
    '/similarity/gene',
    tags=['similarity', 'terms', 'gene'],
    response_description='Similarity score',
    response_model=models.Batch_Similarity_Score
    )
async def batch_gene_similarity(
    data: models.POST_Gene_Batch,
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
):
    """
    Similarity score between one HPOSet and several OMIM Diseases
    """
    other_sets = []

    for other in data.genes:
        actual_gene = Gene.get(other)

        if actual_gene is None:
            hpos = ''
        else:
            hpos = ','.join([str(x) for x in actual_gene.hpo])

        other_sets.append(
            models.POST_HPOSet(
                set2=hpos,
                name=actual_gene.name
            )
        )

    res = await terms.batch_similarity(
        data=models.POST_Batch(
            set1=data.set1,
            other_sets=other_sets
            ),
        method=method,
        combine=combine,
        kind=kind
    )
    return res


@router.get(
    '/similarity/gene/all',
    tags=['similarity', 'terms', 'gene'],
    response_description='Similarity score',
    response_model=models.Batch_Similarity_Score
    )
async def all_gene_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
):
    """
    Calculate Similarity scores between query set and all genes
    """

    data = models.POST_Gene_Batch(
        set1=set1,
        genes=[x.id for x in Ontology.genes]
    )
    res = await batch_gene_similarity(
        data=data,
        method=method,
        combine=combine,
        kind=kind
    )
    return res
