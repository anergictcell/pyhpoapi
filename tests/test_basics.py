import os
import unittest
from fastapi import HTTPException

from pyhpo import Ontology

from fastapi.testclient import TestClient
from pyhpoapi.server import main
from pyhpoapi import helpers


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


class TestSetGetter(unittest.TestCase):
    def setUp(self):
        folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            'data'
        )
        _ = Ontology(data_folder=folder)

    def test_set(self):
        res = helpers.get_hpo_set("HP:0012,HP:0013")
        self.assertEqual(len(res), 2)

    def test_set_with_ints(self):
        res = helpers.get_hpo_set("12,13")
        self.assertEqual(len(res), 2)

    def test_set_with_spaces(self):
        res = helpers.get_hpo_set("HP:0012, HP:0013 ,HP:0021")
        self.assertEqual(len(res), 3)

    def test_set_missing_term(self):
        with self.assertRaises(HTTPException) as err:
            helpers.get_hpo_set("HP:0012,HP:00130")
        assert err.exception.headers
        self.assertEqual(err.exception.headers.get("X-TermNotFound"), "HP:00130")
        
    def test_set_invalid_term(self):
        with self.assertRaises(HTTPException) as err:
            helpers.get_hpo_set("HP:0012,HP:x13")
        assert err.exception.headers
        self.assertEqual(err.exception.headers.get("X-TermNotFound"), "HP:x13")

        with self.assertRaises(HTTPException) as err:
            helpers.get_hpo_set("HP:0012,foobar")
        assert err.exception.headers
        self.assertEqual(err.exception.headers.get("X-TermNotFound"), "foobar")

        with self.assertRaises(HTTPException) as err:
            helpers.get_hpo_set("HP:0012,122")
        assert err.exception.headers
        self.assertEqual(err.exception.headers.get("X-TermNotFound"), "122")
