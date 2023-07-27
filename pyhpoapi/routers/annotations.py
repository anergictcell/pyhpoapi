from fastapi import APIRouter, HTTPException, Path, Query

from pyhpo import Ontology
from pyhpo.annotations import Gene, Omim
from pyhpo import HPOSet

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
) -> dict:
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
    except (KeyError, RuntimeError):
        raise HTTPException(
            status_code=404,
            detail='OMIM disease does not exist'
        )
    try:
        res['hpo'] = [
            Ontology.get_hpo_object(int(x)).toJSON()
            for x in res['hpo']
        ]
    except (KeyError, RuntimeError):
        pass
    return res


@router.get(
    '/gene/{gene_id}',
    tags=['gene'],
    response_description='Gene',
    response_model=models.Gene
)
async def gene(
    gene_id: str = Path(..., example='GBA'),
    verbose: bool = False
) -> dict:
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
        res['hpo'] = [
            Ontology.get_hpo_object(int(x)).toJSON()
            for x in res['hpo']
        ]
    except (KeyError, RuntimeError):
        pass
    return res


@router.get(
    '/similarity/omim',
    tags=['similarity', 'terms', 'disease'],
    response_description='Similarity score for OMIM Diseases',
    response_model=models.SimilarityScore_Omim
    )
async def omim_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    omim: int = Query(..., example=230800),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Similarity score between one HPOSet and an OMIM Disease
    """
    hposet = get_hpo_set(set1)
    try:
        disease = Omim.get(omim)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="OMIM disease does not exist"
        )
    set2 = HPOSet.from_queries([int(x) for x in disease.hpo])

    try:
        return {
            'set1': hposet.toJSON(),
            'set2': set2.toJSON(),
            'omim': disease.toJSON(),
            'similarity': hposet.similarity(
                set2,
                kind=kind,
                method=method,
                combine=combine
            )
        }
    except NotImplementedError:
        raise HTTPException(
            status_code=400,
            detail="The similarity method is not properly implemented"
            )
    except RuntimeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid `method` or `combine` parameter"
            )
    except AttributeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid information content kind specified"
            )



@router.post(
    '/similarity/omim',
    tags=['similarity', 'terms', 'disease'],
    response_description='Similarity score',
    response_model=models.SimilarityScore_Batch
    )
async def batch_omim_similarity(
    data: models.PostBody_Similarity_Omim,
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Similarity score between one HPOSet and several OMIM Diseases
    """
    other_sets = []

    for other in data.omim_diseases:
        try:
            disease = Omim.get(other)
            hpos = ','.join([str(x) for x in disease.hpo])
        except KeyError:
            hpos = f"unknown Omim disease {other}"

        other_sets.append(
            models.NamedHpoSet(
                set2=hpos,
                name=str(other)
            )
        )

    res = await terms.batch_similarity(
        data=models.PostBody_HpoSets(
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
    response_model=models.SimilarityScore_Batch
    )
async def all_omim_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Calculate Similarity scores between query set and all OMIM diseases
    """

    data = models.PostBody_Similarity_Omim(
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
    response_description='Similarity score for genes',
    response_model=models.SimilarityScore_Gene
    )
async def gene_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    gene: str = Query(..., example='GBA'),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Similarity score between one HPOSet and an OMIM Disease
    """
    hposet = get_hpo_set(set1)
    try:
        actual_gene = Gene.get(gene)
    except KeyError:
        raise HTTPException(status_code=404, detail="Gene does not exist")
    set2 = HPOSet.from_queries([int(x) for x in actual_gene.hpo])

    try:
        return {
            'set1': hposet.toJSON(),
            'set2': set2.toJSON(),
            'gene': actual_gene.toJSON(),
            'similarity': hposet.similarity(
                set2,
                kind=kind,
                method=method,
                combine=combine
            )
        }
    except NotImplementedError:
        raise HTTPException(
            status_code=400,
            detail="The similarity method is not properly implemented"
            )
    except RuntimeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid `method` or `combine` parameter"
            )
    except AttributeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid information content kind specified"
            )


@router.post(
    '/similarity/gene',
    tags=['similarity', 'terms', 'gene'],
    response_description='Similarity score',
    response_model=models.SimilarityScore_Batch
    )
async def batch_gene_similarity(
    data: models.PostBody_Similarity_Gene,
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Similarity score between one HPOSet and several OMIM Diseases
    """
    other_sets = []

    for other in data.genes:
        try:
            actual_gene = Gene.get(other)
            hpos = ','.join([str(x) for x in actual_gene.hpo])
        except KeyError:
            hpos = f"unknown gene {other}"

        other_sets.append(
            models.NamedHpoSet(
                set2=hpos,
                name=other
            )
        )

    res = await terms.batch_similarity(
        data=models.PostBody_HpoSets(
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
    response_model=models.SimilarityScore_Batch
    )
async def all_gene_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Calculate Similarity scores between query set and all genes
    """

    data = models.PostBody_Similarity_Gene(
        set1=set1,
        genes=[x.name for x in Ontology.genes]
    )
    res = await batch_gene_similarity(
        data=data,
        method=method,
        combine=combine,
        kind=kind
    )
    return res
