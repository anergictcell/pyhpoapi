import os
import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from pyhpoapi.server import main

from pyhpo import Ontology
from pyhpo.annotations import Gene, Omim
from pyhpo import HPOSet


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
        set1 = 'HP:0000011,HP:0000021'
        set2 = 'HP:0000012,HP:0000031'
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
            [{
                'int': 11,
                'id': 'HP:0000011',
                'name': 'Test child level 1-1'
            }, {
                'int': 21,
                'id': 'HP:0000021',
                'name': 'Test child level 2-1'
            }]
        )
        self.assertEqual(
            res['set2'],
            [{
                'int': 12,
                'id': 'HP:0000012',
                'name': 'Test child level 1-2'
            }, {
                'int': 31,
                'id': 'HP:0000031',
                'name': 'Test child level 3'
            }]
        )
        self.assertIsInstance(res['similarity'], float)
        self.assertGreater(
            res['similarity'],
            0
        )

        set3 = 'HP:0000031,HP:0000041'
        res2 = client.get(
            '/terms/similarity?set1={}&set2={}&method=graphic'.format(
                set3, set3)
        ).json()
        self.assertEqual(
            res2['similarity'],
            1
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
        set1 = 'HP:0000013,HP:0000021'
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
        set1 = 'HP:0000013,HP:0000021'
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
        set1 = 'HP:0000041,HP:0000031'
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
        set1 = 'HP:0000041,HP:0000031'
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
        set1 = 'HP:0000041,HP:0000031'
        mock_model.enrichment = MagicMock(
            return_value=[{
                'item': Gene(12, symbol='G1'),
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
        set1 = 'HP:0000041,HP:0000031'
        mock_model.enrichment = MagicMock(
            return_value=[
                {
                    'item': Gene(12, symbol='G1'),
                    'count': 12,
                    'enrichment': 0.4
                },
                {
                    'item': Gene(15, symbol='G2'),
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
        set1 = 'HP:0000041,HP:0000031'
        mock_model.enrichment = MagicMock(
            return_value=[{
                'item': Omim(12, name='D1'),
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
        set1 = 'HP:0000041,HP:0000031'
        mock_model.enrichment = MagicMock(
            return_value=[
                {
                    'item': Omim(12, name='D1'),
                    'count': 12,
                    'enrichment': 0.4
                },
                {
                    'item': Omim(15, name='D2'),
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


class SimilarityBatchTests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_batch_similarity(self):
        data = {
            'set1': 'HP:0000031,HP:0000041',
            'other_sets': [
                {'set2': 'HP:0000012,HP:0000031', 'name': 'Test1'},
                {'set2': 'HP:0000031,HP:0000041', 'name': 'Test2'}
            ]
        }
        response = client.post('/terms/similarity', json=data).json()

        self.assertEqual(
            [x['id'] for x in response['set1']],
            ['HP:0000031', 'HP:0000041']
        )


    def test_backwards_compatible_trailing_slash(self):
        """
        In version 1.0.0 there was an unitended trailing slash on the
        ``/terms/similarity`` endpoint (``/terms/similarity/``)
        """
        data = {
            'set1': 'HP:0000031,HP:0000041',
            'other_sets': [
                {'set2': 'HP:0000012,HP:0000031', 'name': 'Test1'}
            ]
        }
        response = client.post('/terms/similarity/', json=data).json()

        self.assertEqual(
            [x['id'] for x in response['set1']],
            ['HP:0000031', 'HP:0000041']
        )

    def test_batch_similarity_error(self):
        data = {
            'set1': 'HP:0000031,HP:0000041,foobar',
            'other_sets': [
                {'set2': 'HP:0000012,HP:0000031', 'name': 'Test1'},
                {'set2': 'HP:0000031,HP:0000041', 'name': 'Test2'}
            ]
        }
        response = client.post('/terms/similarity', json=data)

        self.assertEqual(
            response.status_code,
            400
        )
        self.assertEqual(
            response.json()['detail'],
            'Invalid HPO Term identifier in query'
        )

    def test_batch_similarity_invalid_method(self):
        data = {
            'set1': 'HP:0000031,HP:0000041',
            'other_sets': [
                {'set2': 'HP:0000012,HP:0000031', 'name': 'Test1'},
                {'set2': 'HP:0000031,HP:0000041', 'name': 'Test2'}
            ]
        }
        response = client.post('/terms/similarity?method=invalid', json=data)

        self.assertEqual(
            response.status_code,
            400
        )
        self.assertEqual(
            response.json()['detail'],
            'Invalid `method` or `combine` parameter'
        )

    def test_batch_similarity_invalid_combine(self):
        data = {
            'set1': 'HP:0000031,HP:0000041',
            'other_sets': [
                {'set2': 'HP:0000012,HP:0000031', 'name': 'Test1'},
                {'set2': 'HP:0000031,HP:0000041', 'name': 'Test2'}
            ]
        }
        response = client.post('/terms/similarity?combine=invalid', json=data)

        self.assertEqual(
            response.status_code,
            400
        )
        self.assertEqual(
            response.json()['detail'],
            'Invalid `method` or `combine` parameter'
        )

    def test_batch_similarity_invalid_information_content(self):
        data = {
            'set1': 'HP:0000031,HP:0000041',
            'other_sets': [
                {'set2': 'HP:0000012,HP:0000031', 'name': 'Test1'},
                {'set2': 'HP:0000031,HP:0000041', 'name': 'Test2'}
            ]
        }
        response = client.post('/terms/similarity?kind=invalid', json=data)

        self.assertEqual(
            response.status_code,
            400
        )
        self.assertEqual(
            response.json()['detail'],
            'Invalid information content kind specified'
        )

    def test_batch_similarity_skipping_set2(self):
        data = {
            'set1': 'HP:0000031,HP:0000041',
            'other_sets': [
                {'set2': 'HP:0000012,HP:0000031,foobar', 'name': 'Test1'},
                {'set2': 'HP:0000031,HP:0000041', 'name': 'Test2'}
            ]
        }
        response = client.post('/terms/similarity', json=data)

        self.assertEqual(
            response.status_code,
            200
        )

        res = response.json()
        self.assertEqual(
            res['other_sets'][0]['error'],
            'foobar'
        )
        self.assertIsNone(res['other_sets'][0]['similarity'])

        self.assertIsNone(res['other_sets'][1]['error'])

        self.assertIsNotNone(
            res['other_sets'][1]['similarity']
        )


class HPOSuggestionTests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    @patch('pyhpoapi.routers.terms.gene_model')
    @patch('pyhpoapi.routers.terms.omim_model')
    @patch('pyhpoapi.routers.terms.hpo_model_genes')
    @patch('pyhpoapi.routers.terms.hpo_model_omim')
    def test_hpo_suggest(
        self,
        mock_hpo_omim,
        mock_hpo_gene,
        mock_omim_model,
        mock_gene_model,
    ):
        mock_gene_model.enrichment = MagicMock(
            return_value=[{
                'item': Gene(12, symbol='G1'),
                'count': 12,
                'enrichment': 0.4
            }])

        mock_omim_model.enrichment = MagicMock(
            return_value=[
                {
                    'item': Omim(12, name='D1'),
                    'count': 12,
                    'enrichment': 0.4
                },
                {
                    'item': Omim(15, name='D2'),
                    'count': 10,
                    'enrichment': 0.8
                }
            ])

        mock_hpo_gene.enrichment = MagicMock(
            return_value=[{
                'hpo': x,
                'count': int(x),
                'enrichment': int(x)/10
            } for x in Ontology]
        )

        mock_hpo_omim.enrichment = MagicMock(
            return_value=[{
                'hpo': x,
                'count': int(x),
                'enrichment': int(x)/10
            } for x in Ontology]
        )

        set1 = 'HP:0000011,HP:0000021'
        response = client.get(f'/terms/suggest?set1={set1}')
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(
            len(res),
            len(Ontology) - 2
        )

        response = client.get(
            f'/terms/suggest?set1={set1}&n_genes=0&n_omim=0'
        ).json()
        self.assertEqual(
            len(response),
            0
        )

        response = client.get(
            f'/terms/suggest?set1={set1}&limit=2'
        ).json()
        self.assertEqual(
            len(response),
            2
        )



class HierarchyTests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_hierarchy(self):
        set1 = 'HP:0000012,HP:0000013,HP:0000021'
        res = client.get(f'/terms/hierarchy?set1={set1}').json()

        self.assertEqual(len(res), 4)

