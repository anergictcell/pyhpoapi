import os
import unittest

from pyhpo import Ontology

from fastapi.testclient import TestClient
from pyhpoapi.server import main

client = TestClient(main())


class OmimTests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_single_omim(self):
        response = client.get('/omim/600001')
        self.assertEqual(
            response.json(),
            {'id': 600001, 'name': 'Disease 1', 'hpo': None}
        )

        response = client.get('/omim/600001?verbose=True')
        self.assertIsNot(
            response.json()['hpo'],
            None
        )

    def test_missing_omim(self):
        response = client.get('/omim/600011')
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            response.json(),
            {'detail': 'OMIM disease does not exist'}
        )

    def test_omim_similarity(self):
        response = client.get(
            '/similarity/omim?set1=HP:0000021,HP:0000013,HP:0000031&omim=600001'
        )
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('set2', res)
        self.assertIn('omim', res)
        self.assertIn('similarity', res)
        self.assertEqual(len(res['set1']), 3)
        self.assertEqual(len(res['set2']), 2)

        response = client.get(
            '/similarity/omim?set1=HP:0000021,HP:0000013,HP:0000031&omim=6666'
        )
        res = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            res,
            {'detail': 'OMIM disease does not exist'}
        )

    def test_omim_batch_similarity(self):
        data = {
            'set1': 'HP:0000021,HP:0000013,HP:0000031',
            'omim_diseases': [600001, 600002]
        }
        response = client.post('/similarity/omim', json=data)
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('other_sets', res)
        self.assertEqual(len(res['set1']), 3)
        self.assertEqual(len(res['other_sets']), 2)

    def test_all_omim_batch_similarity(self):
        response = client.get('/similarity/omim/all?set1=HP:0000021,HP:0000013,HP:0000031')
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('other_sets', res)
        self.assertEqual(len(res['set1']), 3)
        self.assertEqual(len(res['other_sets']), 2)

    def test_omim_batch_similarity_missing_diseases(self):
        data = {
            'set1': 'HP:0000021,HP:0000013,HP:0000031',
            'omim_diseases': [600001, 600002, 1234]
        }
        response = client.post('/similarity/omim', json=data)
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('other_sets', res)
        self.assertEqual(len(res['set1']), 3)
        self.assertEqual(len(res['other_sets']), 3)

        self.assertIsNone(res['other_sets'][0]['error'])
        self.assertIsNotNone(res['other_sets'][0]['similarity'])
        self.assertIsNone(res['other_sets'][1]['error'])
        self.assertIsNotNone(res['other_sets'][1]['similarity'])
        self.assertIsNotNone(res['other_sets'][2]['error'])
        self.assertIsNone(res['other_sets'][2]['similarity'])


class GeneTests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_single_gene(self):
        response = client.get('/gene/Gene1')
        self.assertEqual(
            response.json(),
            {'id': 1, 'name': 'Gene1', 'symbol': 'Gene1', 'hpo': None}
        )

        response = client.get('/gene/Gene1?verbose=True')
        self.assertIsNot(
            response.json()['hpo'],
            None
        )

    def test_missing_gene(self):
        response = client.get('/gene/27')
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            response.json(),
            {'detail': 'Gene does not exist'}
        )

    def test_gene_similarity(self):
        response = client.get(
            '/similarity/gene?set1=HP:0000021,HP:0000013,HP:0000031&gene=Gene1'
        )
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('set2', res)
        self.assertIn('gene', res)
        self.assertIn('similarity', res)
        self.assertEqual(len(res['set1']), 3)
        self.assertEqual(len(res['set2']), 2)

        response = client.get(
            '/similarity/gene?set1=HP:0000021,HP:0000013,HP:0000031&gene=FooBar'
        )
        res = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            res,
            {'detail': 'Gene does not exist'}
        )

    def test_gene_batch_similarity(self):
        data = {
            'set1': 'HP:0000041,HP:0000031',
            'genes': ['Gene1', 'Gene2']
        }
        response = client.post('/similarity/gene', json=data)
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('other_sets', res)
        self.assertEqual(len(res['set1']), 2)
        self.assertEqual(len(res['other_sets']), 2)

    def test_all_gene_batch_similarity(self):
        response = client.get('/similarity/gene/all?set1=HP:0000041,HP:0000031')
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('other_sets', res)
        self.assertEqual(len(res['set1']), 2)
        self.assertEqual(len(res['other_sets']), 2)

    def test_omim_batch_similarity_missing_diseases(self):
        data = {
            'set1': 'HP:0000041,HP:0000031',
            'genes': ['Gene1', 'Gene2', 'FooBar']
        }
        response = client.post('/similarity/gene', json=data)
        res = response.json()
        self.assertIn('set1', res)
        self.assertIn('other_sets', res)
        self.assertEqual(len(res['set1']), 2)
        self.assertEqual(len(res['other_sets']), 3)

        self.assertIsNone(res['other_sets'][0]['error'])
        self.assertIsNotNone(res['other_sets'][0]['similarity'])
        self.assertIsNone(res['other_sets'][1]['error'])
        self.assertIsNotNone(res['other_sets'][1]['similarity'])
        self.assertIsNotNone(res['other_sets'][2]['error'])
        self.assertIsNone(res['other_sets'][2]['similarity'])
