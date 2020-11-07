from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class Information_Content(BaseModel):
    gene: float
    omim: float
    orpha: float
    decipher: float

    class Config:
        schema_extra = {
            'omim': 5.528020005103167,
            'gene': 4.915866634310163,
            'orpha': 6.491229223514548,
            'decipher': 0
        }


class HPO(BaseModel):
    int: int
    id: str
    name: str
    definition: Optional[str]
    comment: Optional[str]
    xref: Optional[List[str]]
    is_a: Optional[List[str]]
    ic: Optional[Information_Content]

    class Config:
        schema_extra = {
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


class HPOSimple(BaseModel):
    int: int
    id: str
    name: str

    class Config:
        schema_extra = {
            'example': {
                'int': 7401,
                'id': 'HP:0007401',
                'name': 'Macular atrophy',
                }
            }


class HPONeighbours(BaseModel):
    parents: List[HPO]
    children: List[HPO]
    neighbours: List[HPO]


class Omim(BaseModel):
    id: int
    name: str
    hpo: Optional[List[HPO]]

    class Config:
        schema_extra = {
            'example': {
                'id': 230800,
                'name': 'GAUCHER DISEASE, TYPE I'
            }
        }


class Gene(BaseModel):
    id: int
    name: str
    symbol: str
    hpo: Optional[List[HPO]]

    class Config:
        schema_extra = {
            'example': {
                'id': 2629,
                'name': 'GBA',
                'symbol': 'GBA'
            }
        }


class Similarity_Score(BaseModel):
    set1: List[HPOSimple]
    set2: List[HPOSimple]
    similarity: float

    class Config:
        schema_extra = {
            'example': {
                'set1': [HPOSimple.Config.schema_extra['example']],
                'set2': [HPOSimple.Config.schema_extra['example']],
                'similarity': 0.3422332
            }
        }


class Similarity_Score_OMIM(BaseModel):
    set1: List[HPOSimple]
    set2: List[HPOSimple]
    omim: Omim
    similarity: float

    class Config:
        schema_extra = {
            'example': {
                'set1': [HPOSimple.Config.schema_extra['example']],
                'set2': [HPOSimple.Config.schema_extra['example']],
                'omim': Omim.Config.schema_extra['example'],
                'similarity': 0.3422332
            }
        }


class Similarity_Score_Gene(BaseModel):
    set1: List[HPOSimple]
    set2: List[HPOSimple]
    gene: Gene
    similarity: float

    class Config:
        schema_extra = {
            'example': {
                'set1': [HPOSimple.Config.schema_extra['example']],
                'set2': [HPOSimple.Config.schema_extra['example']],
                'gene': Gene.Config.schema_extra['example'],
                'similarity': 0.3422332
            }
        }


class Batch_Similarity_Set(BaseModel):
    name: str
    similarity: Optional[float]
    error: Optional[str]

    class Config:
        schema_extra = {
            'example': {
                'name': 'Comparison-Set 123',
                'similarity': 0.3763421567579537,
                'error': None
            }
        }


class Batch_Similarity_Score(BaseModel):
    set1: List[HPOSimple]
    other_sets: List[Batch_Similarity_Set]

    class Config:
        schema_extra = {
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
                    Batch_Similarity_Set.Config.schema_extra['example'],
                    Batch_Similarity_Set.Config.schema_extra['example']
                ]
            }
        }


class POST_OMIM_Batch(BaseModel):
    set1: str
    omim_diseases: List[int]

    class Config:
        schema_extra = {
            "example": {
                "set1": "HP:0007401,HP:0010885,HP:0006530",
                "omim_diseases": [230800, 230900, 231000, 231005, 608013]
            }
        }


class POST_Gene_Batch(BaseModel):
    set1: str
    genes: List[str]

    class Config:
        schema_extra = {
            "example": {
                "set1": "HP:0007401,HP:0010885,HP:0006530",
                "genes": ['GBA', 'EZH2']
            }
        }


class Similarity_Method(Enum):
    resnik = 'resnik'
    lin = 'lin'
    jc = 'jc'
    jc2 = 'jc2'
    rel = 'rel'
    ic = 'ic'
    graphic = 'graphic'
    dist = 'dist'
    equal = 'equal'


class Combination_Method(Enum):
    funSimAvg = 'funSimAvg'
    funSimMax = 'funSimMax'
    BMA = 'BMA'


class POST_HPOSet(BaseModel):
    """
    Defines the POST body for an HPO Set
    """
    set2: str
    name: str


class POST_Batch(BaseModel):
    set1: str
    other_sets: List[POST_HPOSet]

    class Config:
        schema_extra = {
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
