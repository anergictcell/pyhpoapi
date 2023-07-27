from typing import List, Optional
from pydantic import BaseModel


class InformationContent(BaseModel):
    gene: float
    omim: float
    orpha: float
    decipher: float

    class Config:
        json_schema_extra = {
            'omim': 5.528020005103167,
            'gene': 4.915866634310163,
            'orpha': 6.491229223514548,
            'decipher': 0
        }


class HpoTerm(BaseModel):
    int: int
    id: str
    name: str
    definition: Optional[str] = None
    comment: Optional[str] = None
    synonym: Optional[List[str]] = None
    xref: Optional[List[str]] = None
    is_a: Optional[List[str]] = None
    ic: Optional[InformationContent] = None

    class Config:
        json_schema_extra = {
            'example': {
                'int': 7401,
                'id': 'HP:0007401',
                'name': 'Macular atrophy',
                'definition': (
                    '"Well-demarcated area(s) of partial or complete '
                    'depigmentation in the macula, reflecting atrophy '
                    'of the retinal pigment epithelium with associated '
                    'retinal photoreceptor loss." [ORCID:0000-0003-0986-4123]'
                ),
                'comment': None,
                'synonym': [],
                'xref': [
                    'MSH:D057088',
                    'SNOMEDCT_US:238828009',
                    'UMLS:C1288283'
                ],
                'is_a': [
                    'HP:0000608 ! Macular degeneration',
                    'HP:0001105 ! Retinal atrophy'
                ],
                'ic': {
                    'omim': 5.528020005103167,
                    'gene': 4.915866634310163,
                    'orpha': 6.491229223514548,
                    'decipher': 0
                }
            }
        }


class HpoTermMinimal(BaseModel):
    int: int
    id: str
    name: str

    class Config:
        json_schema_extra = {
            'example': {
                'int': 7401,
                'id': 'HP:0007401',
                'name': 'Macular atrophy',
                }
            }


class HpoNeighborTerms(BaseModel):
    parents: List[HpoTerm]
    children: List[HpoTerm]
    neighbours: List[HpoTerm]


class Omim(BaseModel):
    id: int
    name: str
    hpo: Optional[List[HpoTerm]] = None

    class Config:
        json_schema_extra = {
            'example': {
                'id': 230800,
                'name': 'GAUCHER DISEASE, TYPE I'
            }
        }


class Gene(BaseModel):
    id: int
    name: str
    symbol: str
    hpo: Optional[List[HpoTerm]] = None

    class Config:
        json_schema_extra = {
            'example': {
                'id': 2629,
                'name': 'GBA',
                'symbol': 'GBA'
            }
        }


class SimilarityScore(BaseModel):
    set1: List[HpoTermMinimal]
    set2: List[HpoTermMinimal]
    similarity: float

    class Config:
        json_schema_extra = {
            'example': {
                'set1': [HpoTermMinimal.Config.json_schema_extra['example']],
                'set2': [HpoTermMinimal.Config.json_schema_extra['example']],
                'similarity': 0.3422332
            }
        }


class SimilarityScore_Omim(BaseModel):
    set1: List[HpoTermMinimal]
    set2: List[HpoTermMinimal]
    omim: Omim
    similarity: float

    class Config:
        json_schema_extra = {
            'example': {
                'set1': [HpoTermMinimal.Config.json_schema_extra['example']],
                'set2': [HpoTermMinimal.Config.json_schema_extra['example']],
                'omim': Omim.Config.json_schema_extra['example'],
                'similarity': 0.3422332
            }
        }


class SimilarityScore_Gene(BaseModel):
    set1: List[HpoTermMinimal]
    set2: List[HpoTermMinimal]
    gene: Gene
    similarity: float

    class Config:
        json_schema_extra = {
            'example': {
                'set1': [HpoTermMinimal.Config.json_schema_extra['example']],
                'set2': [HpoTermMinimal.Config.json_schema_extra['example']],
                'gene': Gene.Config.json_schema_extra['example'],
                'similarity': 0.3422332
            }
        }


class SimilarityScore_SingleSet(BaseModel):
    name: str
    similarity: Optional[float] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            'example': {
                'name': 'Comparison-Set 123',
                'similarity': 0.3763421567579537,
                'error': None
            }
        }


class SimilarityScore_Batch(BaseModel):
    set1: List[HpoTermMinimal]
    other_sets: List[SimilarityScore_SingleSet]

    class Config:
        json_schema_extra = {
            'example': {
                'set1': [{
                    'int': 7401,
                    'id': 'HP:0007401',
                    'name': 'Macular atrophy'
                }, {
                    'int': 6530,
                    'id': 'HP:0006530',
                    'name': 'Interstitial pulmonary abnormality'
                }, {
                    'int': 10885,
                    'id': 'HP:0010885',
                    'name': 'Avascular necrosis'
                }],
                'other_sets': [
                    SimilarityScore_SingleSet.Config.json_schema_extra['example'],
                    SimilarityScore_SingleSet.Config.json_schema_extra['example']
                ]
            }
        }


class PostBody_Similarity_Omim(BaseModel):
    set1: str
    omim_diseases: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "set1": "HP:0007401,HP:0010885,HP:0006530",
                "omim_diseases": [230800, 230900, 231000, 231005, 608013]
            }
        }


class PostBody_Similarity_Gene(BaseModel):
    set1: str
    genes: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "set1": "HP:0007401,HP:0010885,HP:0006530",
                "genes": ['GBA', 'EZH2']
            }
        }


class NamedHpoSet(BaseModel):
    """
    Defines the POST body for an HPO Set
    """
    set2: str
    name: str


class PostBody_HpoSets(BaseModel):
    set1: str
    other_sets: List[NamedHpoSet]

    class Config:
        json_schema_extra = {
            "example": {
                "set1": "HP:0007401,HP:0010885,HP:0006530",
                "other_sets": [
                    {
                        "set2": "HP:0200070,HP:0002754,HP:0031630",
                        "name": "Comparison-Set 123"
                    }, {
                        "set2": "HP:0012332,HP:0002094,HP:0012337,HP:0002098",
                        "name": "Comparison-Set FooBar"
                    }
                ]
            }
        }
