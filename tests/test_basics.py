import os
import unittest

from pyhpo.ontology import Ontology

from fastapi.testclient import TestClient
from pyhpoapi.server import main


client = TestClient(main())


class StaticAPITests(unittest.TestCase):
    def test_logo(self):
        response = client.get('/logo')
        assert response.status_code == 200


class TestHelper(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_invalid_hpo_terms(self):
        set1 = 'HP:0041,HP:0081'
        response = client.get(
            '/terms/union/genes?set1={}'.format(
                set1)
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'detail': 'Invalid HPO Term identifier in query'}
        )
        self.assertIn(
            'x-termnotfound',
            response.headers
        )
        self.assertEqual(
            response.headers['x-termnotfound'],
            'HP:0081'
            )

    def test_invalid_set_query(self):
        set1 = 'HP:0041,foobar'
        response = client.get(
            '/terms/union/genes?set1={}'.format(
                set1)
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'detail': 'Invalid HPO Term identifier in query'}
        )
