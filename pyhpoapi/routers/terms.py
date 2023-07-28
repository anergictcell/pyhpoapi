from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional

from pyhpo import Ontology
from pyhpo.stats import EnrichmentModel
try:
    from pyhpo.stats import HPOEnrichment
except ImportError:
    from pyhpoapi.helpers import MockHPOEnrichment as HPOEnrichment

from pyhpo import HPOTerm

from pyhpoapi.helpers import get_hpo_set
from pyhpoapi import models

router = APIRouter()

gene_model: Optional[EnrichmentModel] = None
omim_model: Optional[EnrichmentModel] = None
hpo_model_genes: Optional[HPOEnrichment] = None
hpo_model_omim: Optional[HPOEnrichment] = None


@router.get(
    '/search/{query}',
    tags=['terms'],
    response_description='List of HPOTerms',
    response_model=List[models.HpoTerm],
    response_model_exclude_none=True
)
async def HPO_search(
    query: str,
    verbose: bool = False,
    limit: int = 10,
    offset: int = 0
) -> List[dict]:
    """
    Get all HPOTerms via substring match.
    This search searches in name, alternative names and synonyms

    Parameters
    ----------
    query: str
        The substring to search for
    verbose: bool, default False
        Show more info about the HPOTerm
    limit: int, default 10
        The number of results to return
    offset: int, default 0
        For paging, the offset of the first result to show

    Returns
    -------
    dict
        Array of HPOTerms

    """
    res = []
    for idx, term in enumerate(Ontology.search(query)):
        if idx > (offset + limit-1):
            break
        if idx < offset:
            continue
        res.append(term)
    return [t.toJSON(bool(verbose)) for t in res]


@router.get(
    '/intersect/omim',
    tags=['annotations'],
    response_description='List of OMIM Diseases',
    response_model=List[models.Omim]

)
async def intersecting_OMIM_diseases(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530')
) -> List[dict]:
    """
    Get all OMIM Diseases, associated with several HPOTerms.
    All diseases are returned that are associated with any of the
    provided HPOTerms

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers

    Returns
    -------
    array
        Array of OMIM diseases
    """
    hposet = get_hpo_set(set1)
    diseases = hposet.omim_diseases()
    for term in hposet:
        diseases = diseases & term.omim_diseases
    return [
            d.toJSON()
            for d in diseases
        ]


@router.get(
    '/intersect/genes',
    tags=['annotations'],
    response_description='List of Genes',
    response_model=List[models.Gene]
)
async def intersecting_genes(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530')
) -> List[dict]:
    """
    Get all Genes, associated with several HPOTerms.
    All genes are returned that are associated with any of the
    provided HPOTerms

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers

    Returns
    -------
    array
        Array of Genes
    """
    hposet = get_hpo_set(set1)
    genes = hposet.all_genes()
    for term in hposet:
        genes = genes & term.genes
    return [
            g.toJSON()
            for g in genes
        ]


@router.get(
    '/union/omim',
    tags=['annotations'],
    response_description='List of OMIM Diseases',
    response_model=List[models.Omim]
)
async def union_OMIM_diseases(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530')
) -> List[dict]:
    """
    Get all OMIM Diseases, associated with several HPOTerms.
    Only diseases are returned that are associated with all provided HPOTerms

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers

    Returns
    -------
    array
        Array of OMIM diseases
    """
    hposet = get_hpo_set(set1)
    diseases = hposet.omim_diseases()
    return [
            d.toJSON()
            for d in diseases
        ]


@router.get(
    '/union/genes',
    tags=['annotations'],
    response_description='List of Genes',
    response_model=List[models.Gene]
)
async def union_genes(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530')
) -> List[dict]:
    """
    Get all Genes, associated with several HPOTerms.
    Only genes are returned that are associated with all provided HPOTerms

    You can look up terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers

    Returns
    -------
    array
        Array of Genes
    """
    hposet = get_hpo_set(set1)
    genes = hposet.all_genes()
    return [
            g.toJSON()
            for g in genes
        ]


@router.get(
    '/similarity',
    tags=['similarity'],
    response_description='Similarity score',
    response_model=models.SimilarityScore
)
async def terms_similarity(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    set2: str = Query(..., example='HP:0200070,HP:0002754,HP:0031630'),
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Similarity score of two different HPOSets

    You can identify terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers
    set2: list of int or str
        Comma-separated list of HPOTerm identifiers
    kind: str, default ``None``
        Which kind of information content should be calculated.
        Options are ['omim', 'orpha', 'decipher', 'gene']
        See :func:`pyhpo.HPOTerm.similarity_score` for options

    method: string, default ``None``
        The method to use to calculate the similarity.

        Available options:

        * **resnik** - Resnik P, Proceedings of the 14th IJCAI, (1995)
        * **lin** - Lin D, Proceedings of the 15th ICML, (1998)
        * **jc** - Jiang J, Conrath D, ROCLING X, (1997)
          Implementation according to R source code
        * **jc2** - Jiang J, Conrath D, ROCLING X, (1997)
          Implementation according to paper from R ``hposim`` library
          Deng Y, et. al., PLoS One, (2015)
        * **rel** - Relevance measure - Schlicker A, et.al.,
          BMC Bioinformatics, (2006)
        * **ic** - Information coefficient - Li B, et. al., arXiv, (2010)
        * **graphic** - Graph based Information coefficient -
          Deng Y, et. al., PLoS One, (2015)
        * **dist** - Distance between terms
        * **equal** - Calculates exact matches between both sets

    combine: string, default ``funSimAvg``
        The method to combine similarity measures.

        Available options:

        * **funSimAvg** - Schlicker A, BMC Bioinformatics, (2006)
        * **funSimMax** - Schlicker A, BMC Bioinformatics, (2006)
        * **BMA** - Deng Y, et. al., PLoS One, (2015)

    Returns
    -------
    float
        The similarity score to the other HPOSet
    """
    hposet1 = get_hpo_set(set1)
    hposet2 = get_hpo_set(set2)

    try:
        return {
            'set1': hposet1.toJSON(),
            'set2': hposet2.toJSON(),
            'similarity': hposet1.similarity(
                hposet2,
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



@router.post('/similarity/', include_in_schema=False)
@router.post(
    '/similarity',
    tags=['similarity'],
    response_description='Similarity scores',
    response_model=models.SimilarityScore_Batch
)
async def batch_similarity(
    data: models.PostBody_HpoSets,
    method: str = 'graphic',
    combine: str = 'funSimAvg',
    kind: str = 'omim'
) -> dict:
    """
    Calculate similarity scores between one base and
    several other HPOSets

    You can identify terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    data: PostBody_HpoSets

    kind: str, default ``None``
        Which kind of information content should be calculated.
        Options are ['omim', 'orpha', 'decipher', 'gene']
        See :func:`pyhpo.HPOTerm.similarity_score` for options

    method: string, default ``None``
        The method to use to calculate the similarity.

        Available options:

        * **resnik** - Resnik P, Proceedings of the 14th IJCAI, (1995)
        * **lin** - Lin D, Proceedings of the 15th ICML, (1998)
        * **jc** - Jiang J, Conrath D, ROCLING X, (1997)
          Implementation according to R source code
        * **jc2** - Jiang J, Conrath D, ROCLING X, (1997)
          Implementation according to paper from R ``hposim`` library
          Deng Y, et. al., PLoS One, (2015)
        * **rel** - Relevance measure - Schlicker A, et.al.,
          BMC Bioinformatics, (2006)
        * **ic** - Information coefficient - Li B, et. al., arXiv, (2010)
        * **graphic** - Graph based Information coefficient -
          Deng Y, et. al., PLoS One, (2015)
        * **dist** - Distance between terms
        * **equal** - Calculates exact matches between both sets

    combine: string, default ``funSimAvg``
        The method to combine similarity measures.

        Available options:

        * **funSimAvg** - Schlicker A, BMC Bioinformatics, (2006)
        * **funSimMax** - Schlicker A, BMC Bioinformatics, (2006)
        * **BMA** - Deng Y, et. al., PLoS One, (2015)

    Returns
    -------
    object
        The similarity scores to the other HPOSets
    """
    set1 = get_hpo_set(data.set1)
    other_sets = []
    for other in data.other_sets:
        res = {'name': other.name, 'similarity': 0.0, 'error': None}
        try:
            set2 = get_hpo_set(other.set2)
            res['similarity'] = set1.similarity(
                set2,
                kind=kind,
                method=method,
                combine=combine
            )
        except HTTPException as ex:
            res['similarity'] = None
            if ex.headers:
                res['error'] = ex.headers.get(
                    'X-TermNotFound', 'Unknown error'
                )
            else:
                res['error'] = 'Unknown error'
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

        other_sets.append(res)
    return {
        'set1': set1.toJSON(),
        'other_sets': other_sets
    }


@router.get(
    '/enrichment/genes',
    tags=['enrichment'],
    response_description='Enrichment scores'
)
async def gene_enrichment(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    method: str = 'hypergeom',
    limit: int = 10,
    offset: int = 0
) -> List[dict]:
    """
    Enrichment of genes in an HPOSet

    You can identify terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers
    method: str, default ``hypergeom``
        Algorithm for enrichment calculation
        Options are ['hypergeom']
    limit: int, default 10
        The number of results to return
    offset: int, default 0
        For paging, the offset of the first result to show

    Returns
    -------
    list of dict
        A ordered list with enriched genes
    """
    assert gene_model, 'The Gene Enrichment Model is not defined'
    hposet = get_hpo_set(set1)
    try:
        res = gene_model.enrichment(method, hposet)
    except (NotImplementedError, RuntimeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid parameter"
            )

    return [{
        'gene': x['item'].toJSON(),
        'count': x['count'],
        'enrichment': x['enrichment']
    } for x in res[offset:(limit+offset)]]


@router.get(
    '/enrichment/omim',
    tags=['enrichment'],
    response_description='Enrichment scores'
)
async def omim_enrichment(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    method: str = 'hypergeom',
    limit: int = 10,
    offset: int = 0
) -> List[dict]:
    """
    Enrichment of OMIM diseases in an HPOSet

    You can identify terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers

    method: str, default ``hypergeom``
        Algorithm for enrichment calculation
        Options are ['hypergeom']

    limit: int, default 10
        The number of results to return

    offset: int, default 0
        For paging, the offset of the first result to show

    Returns
    -------
    list of dict
        A ordered list with enriched genes
    """
    assert omim_model, 'The OMIM Enrichment Model is not defined'

    hposet = get_hpo_set(set1)
    try:
        res = omim_model.enrichment(method, hposet)
    except (NotImplementedError, RuntimeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid parameter"
            )

    return [{
        'omim': x['item'].toJSON(),
        'count': x['count'],
        'enrichment': x['enrichment']
    } for x in res[offset:(limit+offset)]]


@router.get('/suggest/', include_in_schema=False)
@router.get(
    '/suggest',
    tags=['enrichment'],
    response_description='HPOTerm list',
    response_model=List[models.HpoTerm]
)
async def hpo_suggest(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530'),
    method: str = 'hypergeom',
    limit: int = 10,
    offset: int = 0,
    n_genes: int = 5,
    n_omim: int = 5
) -> List[dict]:
    """
    Suggest 'similar' HPOterms based on a given list of Terms

    What happens in the background when you call this:

    * Search for the most enriched Genes and OMIM diseases based
      on the provided HPOTerm list (like the enrichment call)
    * Use the enriched genes and diseases and look for enriched
      HPO terms among them

    You can identify terms via:

    * **HPO Identifier**: ``'HP:0000003'``
    * **Term name**: ``'Multicystic kidney dysplasia'``
    * **Integer representation of HPO ID**: ``3``

    Parameters
    ----------
    set1: list of int or str
        Comma-separated list of HPOTerm identifiers

    method: str, default 'hypergeom'
        Enrichment method to use

    limit: int, default 10
        The number of results to return

    offset: int, default 0
        For paging, the offset of the first result to show

    n_genes: int, default 5
        Consider HPO terms from the Top X enriched genes

    n_omim: int, default 5
        Consider HPO terms from the Top X enriched OMIM diseases
    """

    assert gene_model, 'The Gene Enrichment Model is not defined'
    assert omim_model, 'The OMIM Enrichment Model is not defined'
    assert hpo_model_genes, 'The HPO Gene Enrichment Model is not defined'
    assert hpo_model_omim, 'The HPO OMIM Enrichment Model is not defined'

    hposet = get_hpo_set(set1)

    try:
        if n_omim:
            omim_res = hpo_model_omim.enrichment(
                method,
                [x['item'] for x in omim_model.enrichment(method, hposet)[0:n_omim]]
            )
        else:
            omim_res = []
        if n_genes:
            gene_res = hpo_model_genes.enrichment(
                method,
                [x['item'] for x in gene_model.enrichment(method, hposet)[0:n_genes]]
            )
        else:
            gene_res = []
    except NotImplementedError:
        raise HTTPException(
            status_code=404,
            detail="This method is not implemented"
            )
    except RuntimeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid parameter"
            )

    res = sorted(omim_res + gene_res, key=lambda x: x['enrichment'])[offset:]

    hpos: List[HPOTerm] = []
    while len(hpos) < limit and len(res):
        hpo = res.pop(0)['hpo']
        if hpo not in hpos and hpo not in hposet:
            hpos.append(hpo)
    return [x.toJSON() for x in hpos]


@router.get('/hierarchy/', include_in_schema=False)
@router.get(
    '/hierarchy',
    tags=['enrichment'],
    response_description='HPO-Hierachy list'
)
async def hierarchy_graph(
    set1: str = Query(..., example='HP:0007401,HP:0010885,HP:0006530')
) -> List[dict]:
    hposet = get_hpo_set(set1)

    children = set()
    for term in hposet:
        for child in term.children:
            if child not in hposet and child not in children:
                children.add(child)
    for term in hposet:
        children.add(term)

    return [{
        'name': term.name,
        'omim': term.information_content['omim'],
        'gene': term.information_content['gene'],
        'imports': [t.name for t in term.children],
        'diseases': [d.name for d in term.omim_diseases],
        'genes': [g.name for g in term.genes]
    } for term in (children)]
