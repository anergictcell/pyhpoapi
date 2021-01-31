import os
import unittest

from fastapi.testclient import TestClient
from pyhpoapi.server import main

from pyhpo.ontology import Ontology


client = TestClient(main())


class TermAPITests(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_single_term(self):
        response = client.get('/term/HP:0011')
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            response.json(),
            {
                'id': 'HP:0011',
                'int': 11,
                'name': 'Test child level 1-1',
                'comment': None,
                'definition': None,
                'ic': None,
                'is_a': None,
                'xref': None
            }
        )

        response2 = client.get('/term/11')
        self.assertEqual(
            response2.status_code,
            200
        )
        self.assertEqual(
            response.json(),
            response2.json()
        )

    def test_single_term_failure(self):
        response = client.get('/term/HP:000000312')
        self.assertEqual(
            response.status_code,
            404
        )

    def test_single_term_verbose(self):
        response = client.get('/term/HP:0011?verbose=True')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(res['id'], 'HP:0011')
        self.assertEqual(res['int'], 11)
        self.assertEqual(res['name'], 'Test child level 1-1')
        self.assertIsNotNone(res['comment'])
        self.assertIsNotNone(res['definition'])
        self.assertIsNotNone(res['ic'])
        self.assertIsNotNone(res['is_a'])
        self.assertIsNotNone(res['xref'])

    def test_single_parent_terms(self):
        response = client.get('/term/HP:0011/parents')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        term = res[0]
        self.assertEqual(term['id'], 'HP:0001')
        self.assertEqual(term['int'], 1)
        self.assertEqual(term['name'], 'Test root')
        self.assertIsNone(term['comment'])
        self.assertIsNone(term['definition'])
        self.assertIsNone(term['ic'])
        self.assertIsNone(term['is_a'])
        self.assertIsNone(term['xref'])

    def test_single_parent_terms_verbose(self):
        response = client.get('/term/HP:0011/parents?verbose=True')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        term = res[0]
        self.assertEqual(term['id'], 'HP:0001')
        self.assertEqual(term['int'], 1)
        self.assertEqual(term['name'], 'Test root')
        self.assertEqual(term['comment'], 'FooBar')
        self.assertEqual(term['definition'], 'BarFoo')
        self.assertIsNotNone(term['ic'])
        self.assertEqual(term['is_a'], [])
        self.assertEqual(term['xref'], [])

    def test_multi_parent_terms(self):
        response = client.get('/term/HP:0031/parents')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        term = res[0]
        self.assertEqual(term['id'], 'HP:0021')
        self.assertEqual(term['int'], 21)
        self.assertEqual(term['name'], 'Test child level 2-1')
        self.assertIsNone(term['comment'])
        self.assertIsNone(term['definition'])
        self.assertIsNone(term['ic'])
        self.assertIsNone(term['is_a'])
        self.assertIsNone(term['xref'])

        term = res[1]
        self.assertEqual(term['id'], 'HP:0012')
        self.assertEqual(term['int'], 12)
        self.assertEqual(term['name'], 'Test child level 1-2')
        self.assertIsNone(term['comment'])
        self.assertIsNone(term['definition'])
        self.assertIsNone(term['ic'])
        self.assertIsNone(term['is_a'])
        self.assertIsNone(term['xref'])

    def test_no_parent_terms(self):
        response = client.get('/term/HP:0001/parents')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 0)

    def test_single_child_terms(self):
        response = client.get('/term/HP:0011/children')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        term = res[0]
        self.assertEqual(term['id'], 'HP:0021')
        self.assertEqual(term['int'], 21)
        self.assertEqual(term['name'], 'Test child level 2-1')

    def test_multi_child_terms(self):
        response = client.get('/term/HP:0001/children')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]['id'], 'HP:0011')
        self.assertEqual(res[0]['int'], 11)
        self.assertEqual(res[1]['id'], 'HP:0012')
        self.assertEqual(res[1]['int'], 12)
        self.assertEqual(res[2]['id'], 'HP:0013')
        self.assertEqual(res[2]['int'], 13)

    def test_no_child_terms(self):
        response = client.get('/term/HP:0013/children')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 0)

    def test_neighbours_from_parent(self):
        response = client.get('/term/HP:0011/neighbours')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            {x['id'] for x in res['parents']},
            set(['HP:0001'])
        )
        self.assertEqual(
            {x['id'] for x in res['neighbours']},
            set(['HP:0012', 'HP:0013'])
        )
        self.assertEqual(
            {x['id'] for x in res['children']},
            set(['HP:0021'])
        )

    def test_neighbours_from_child(self):
        response = client.get('/term/HP:0021/neighbours')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            {x['id'] for x in res['parents']},
            set(['HP:0011'])
        )
        self.assertEqual(
            {x['id'] for x in res['neighbours']},
            set(['HP:0012'])
        )
        self.assertEqual(
            {x['id'] for x in res['children']},
            set(['HP:0031'])
        )

        # ToDo: Test a neigbour term that comes from a child

    def test_single_genes(self):
        response = client.get('/term/HP:0041/genes')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            1
        )
        self.assertEqual(
            res[0],
            {
                'id': 1,
                'name': 'Gene1',
                'symbol': 'Gene1',
                'hpo': None
            }
        )

    def test_multiple_genes(self):
        response = client.get('/term/HP:0012/genes')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            2
        )
        self.assertEqual(
            {x['id'] for x in res},
            set([1, 2])
        )

    def test_no_genes(self):
        response = client.get('/term/HP:0013/genes')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            0
        )

    def test_single_omim(self):
        response = client.get('/term/HP:0013/omim')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            1
        )
        self.assertEqual(
            res[0],
            {
                'id': 600001,
                'name': 'Disease 1',
                'hpo': None
            }
        )

    def test_multiple_omim(self):
        response = client.get('/term/HP:0021/omim')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            2
        )
        self.assertEqual(
            {x['id'] for x in res},
            set([600001, 600002])
        )

    def test_no_omim(self):
        response = client.get('/term/HP:0041/omim')
        self.assertEqual(
            response.status_code,
            200
        )
        res = response.json()
        self.assertEqual(
            len(res),
            0
        )
