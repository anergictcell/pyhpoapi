import os
import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from pyhpoapi.server import main
from pyhpoapi.routers import terms
from pyhpoapi.models import HPOSimple

from pyhpo.ontology import Ontology
from pyhpo.annotations import GeneSingleton, OmimDisease
from pyhpo.set import HPOSet


client = TestClient(main())


class TermsAPITests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_search(self):
        response = client.get('/terms/search/child')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            6
        )
        self.assertIsNotNone(res[0]['id'])
        self.assertIsNotNone(res[0]['int'])
        self.assertIsNotNone(res[0]['name'])

    def test_limit_search(self):
        response = client.get('/terms/search/child?limit=2')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            2
        )

    def test_search_offset(self):
        response = client.get('/terms/search/child?offset=4')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            2
        )

    def test_similarity(self):
        set1 = 'HP:0011,HP:0021'
        set2 = 'HP:0012,HP:0031'
        with patch.object(
            terms,
            'get_hpo_set',
            side_effect=[
                MagicMock(
                    toJSON=lambda: [
                        HPOSimple.Config.schema_extra['example']
                    ]),
                MagicMock(
                    toJSON=lambda: [
                        HPOSimple.Config.schema_extra['example']
                    ],
                    similarity=lambda: 1.0
                )
            ]
        ) as p:
            response = client.get(
                '/terms/similarity?set1={}&set2={}'.format(
                    set1, set2)
            )
            self.assertEqual(
                response.status_code,
                200
            )
            res = response.json()
            self.assertEqual(
                res['set1'],
                [HPOSimple.Config.schema_extra['example']]
            )
            self.assertEqual(
                res['set1'],
                [HPOSimple.Config.schema_extra['example']]
            )
            self.assertIsInstance(res['similarity'], float)
            self.assertEqual(
                res['similarity'],
                1.0
            )


class TermsAnnotationTests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_intersecting_OMIM_diseases(self):
        set1 = 'HP:0013,HP:0021'
        response = client.get(
            '/terms/intersect/omim?set1={}'.format(
                set1)
        )
        res = response.json()
        self.assertEqual(
            res,
            [{'id': 600001, 'name': 'Disease 1', 'hpo': None}]
        )

    def test_union_OMIM_diseases(self):
        set1 = 'HP:0013,HP:0021'
        response = client.get(
            '/terms/union/omim?set1={}'.format(
                set1)
        )
        res = response.json()
        self.assertEqual(len(res), 2)
        self.assertIn(
            {'id': 600001, 'name': 'Disease 1', 'hpo': None},
            res
        )
        self.assertIn(
            {'id': 600002, 'name': 'Disease 2', 'hpo': None},
            res
        )

    def test_intersecting_genes(self):
        set1 = 'HP:0041,HP:0031'
        response = client.get(
            '/terms/intersect/genes?set1={}'.format(
                set1)
        )
        res = response.json()
        self.assertEqual(
            res,
            [{'id': 1, 'name': 'Gene1', 'symbol': 'Gene1', 'hpo': None}]
        )

    def test_union_genes(self):
        set1 = 'HP:0041,HP:0031'
        response = client.get(
            '/terms/union/genes?set1={}'.format(
                set1)
        )
        res = response.json()
        self.assertEqual(len(res), 2)
        self.assertIn(
            {'id': 2, 'name': 'Gene2', 'symbol': 'Gene2', 'hpo': None},
            res
        )
        self.assertIn(
            {'id': 1, 'name': 'Gene1', 'symbol': 'Gene1', 'hpo': None},
            res
        )

    @patch('pyhpoapi.routers.terms.gene_model')
    def test_single_gene_enrichment(self, mock_model):
        """
        Assuming the gene_model.enrichment method is propery tested
        in the upstream pyhpo package
        """
        set1 = 'HP:0041,HP:0031'
        mock_model.enrichment = MagicMock(
            return_value=[{
                'item': GeneSingleton(idx=12, name='G1'),
                'count': 12,
                'enrichment': 0.4
            }])
        response = client.get(
            '/terms/enrichment/genes?set1={}'.format(
                set1)
        )
        res = response.json()
        mock_model.enrichment.assert_called_with(
            'hypergeom',
            HPOSet.from_serialized('31+41')
        )
        mock_model.enrichment.assert_called_once()
        self.assertEqual(len(res), 1)
        self.assertEqual(
            res[0]['gene'],
            {'id': 12, 'name': 'G1', 'symbol': 'G1'}
        )
        self.assertEqual(res[0]['count'], 12)
        self.assertEqual(res[0]['enrichment'], 0.4)

    @patch('pyhpoapi.routers.terms.gene_model')
    def test_multi_gene_enrichment(self, mock_model):
        """
        Assuming the gene_model.enrichment method is propery tested
        in the upstream pyhpo package
        """
        set1 = 'HP:0041,HP:0031'
        mock_model.enrichment = MagicMock(
            return_value=[
                {
                    'item': GeneSingleton(idx=12, name='G1'),
                    'count': 12,
                    'enrichment': 0.4
                },
                {
                    'item': GeneSingleton(idx=15, name='G2'),
                    'count': 10,
                    'enrichment': 0.8
                }
            ])
        response = client.get(
            '/terms/enrichment/genes?set1={}'.format(
                set1)
        )
        res = response.json()
        mock_model.enrichment.assert_called_with(
            'hypergeom',
            HPOSet.from_serialized('31+41')
        )
        mock_model.enrichment.assert_called_once()
        self.assertEqual(len(res), 2)
        self.assertEqual(
            res[0]['gene'],
            {'id': 12, 'name': 'G1', 'symbol': 'G1'}
        )
        self.assertEqual(res[0]['count'], 12)
        self.assertEqual(res[0]['enrichment'], 0.4)
        self.assertEqual(
            res[1]['gene'],
            {'id': 15, 'name': 'G2', 'symbol': 'G2'}
        )
        self.assertEqual(res[1]['count'], 10)
        self.assertEqual(res[1]['enrichment'], 0.8)

    @patch('pyhpoapi.routers.terms.omim_model')
    def test_single_omim_enrichment(self, mock_model):
        """
        Assuming the gene_model.enrichment method is propery tested
        in the upstream pyhpo package
        """
        set1 = 'HP:0041,HP:0031'
        mock_model.enrichment = MagicMock(
            return_value=[{
                'item': OmimDisease(idx=12, name='D1'),
                'count': 12,
                'enrichment': 0.4
            }])
        response = client.get(
            '/terms/enrichment/omim?set1={}'.format(
                set1)
        )
        res = response.json()
        mock_model.enrichment.assert_called_with(
            'hypergeom',
            HPOSet.from_serialized('31+41')
        )
        mock_model.enrichment.assert_called_once()
        self.assertEqual(len(res), 1)
        self.assertEqual(
            res[0]['omim'],
            {'id': 12, 'name': 'D1'}
        )
        self.assertEqual(res[0]['count'], 12)
        self.assertEqual(res[0]['enrichment'], 0.4)

    @patch('pyhpoapi.routers.terms.omim_model')
    def test_multi_omim_enrichment(self, mock_model):
        """
        Assuming the gene_model.enrichment method is propery tested
        in the upstream pyhpo package
        """
        set1 = 'HP:0041,HP:0031'
        mock_model.enrichment = MagicMock(
            return_value=[
                {
                    'item': OmimDisease(idx=12, name='D1'),
                    'count': 12,
                    'enrichment': 0.4
                },
                {
                    'item': OmimDisease(idx=15, name='D2'),
                    'count': 10,
                    'enrichment': 0.8
                }
            ])
        response = client.get(
            '/terms/enrichment/omim?set1={}'.format(
                set1)
        )
        res = response.json()
        mock_model.enrichment.assert_called_with(
            'hypergeom',
            HPOSet.from_serialized('31+41')
        )
        mock_model.enrichment.assert_called_once()
        self.assertEqual(len(res), 2)
        self.assertEqual(
            res[0]['omim'],
            {'id': 12, 'name': 'D1'}
        )
        self.assertEqual(res[0]['count'], 12)
        self.assertEqual(res[0]['enrichment'], 0.4)
        self.assertEqual(
            res[1]['omim'],
            {'id': 15, 'name': 'D2'}
        )
        self.assertEqual(res[1]['count'], 10)
        self.assertEqual(res[1]['enrichment'], 0.8)
