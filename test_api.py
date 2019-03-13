import unittest
from app import app
import json


class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.headers = {'Content-Type': 'application/json'}

    def test_get_valid(self):
        """
        Test that valid GET requests are processed correctly
        :return:
        """
        response = self.app.get("/actors?name=Bruce Willis")
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue('Bruce Willis' in data)

        response = self.app.get("/actors?name=Bruce Willis&age=80")
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue('Bruce Willis' in data)

        response = self.app.get("/movies?name=The First Deadly Sin&gross=53977250&year=1980")
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue('The First Deadly Sin' in data)

        response = self.app.get("/actors/Bruce Willis")
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue('Bruce Willis' in data)

        response = self.app.get("/movies/The Verdict")
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue('The Verdict' in data)

    def test_get_invalid(self):
        """
        Test that invalid GET requests are processed correctly
        :return:
        """
        response = self.app.get("/actors?name=Bryant Collaguazo")
        self.assertEqual(response.status_code, 400)

        response = self.app.get("/movies?name=The Life of Bryant Collaguazo")
        self.assertEqual(response.status_code, 400)

        response = self.app.get("/movies?year=2098&gross=-20")
        self.assertEqual(response.status_code, 400)

        response = self.app.get("/actors/Bryant Collaguaz")
        self.assertEqual(response.status_code, 404)

        response = self.app.get("/movies/The Life of Bryant Collaguazo")
        self.assertEqual(response.status_code, 404)

    def test_put_valid(self):
        """
        Test that valid PUT requests are processed correctly
        :return:
        """
        data = {'age': 100}
        response = self.app.put('/api/a/actors/Bruce Willis',
                                data=json.dumps(data),
                                headers=self.headers)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['age'], 100)

        data = {'year': 2005}
        response = self.app.put('/api/a/movies/The First Deadly Sin',
                                data=json.dumps(data),
                                headers=self.headers)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['year'], 2005)

    def test_put_invalid(self):
        """
        Test that invalid PUT requests are processed correctly
        :return:
        """
        data = {'age': 100}
        response = self.app.put('/api/a/actors/Bruce Willis',
                                data=data,
                                headers={'Content-Type': 'not_json'})
        self.assertEqual(response.status_code, 400)
        response = self.app.put('/api/a/actors/James Collaguazo',
                                data=json.dumps(data),
                                headers=self.headers)
        self.assertEqual(response.status_code, 404)

        data = {'age': 2005}
        response = self.app.put('/api/a/movies/The First Deadly Sin',
                                data=data,
                                headers={'Content-Type': 'not_json'})
        self.assertEqual(response.status_code, 400)
        response = self.app.put('/api/a/movies/The Life of James Collaguazo',
                                data=json.dumps(data),
                                headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_post_valid(self):
        """
        Test that valid POST requests are processed correctly
        :return:
        """
        data = {'name': 'Bryant Collaguazo', 'age': 100, 'gross': 100}
        response = self.app.post('/api/a/actors/',
                                 data=json.dumps(data),
                                 headers=self.headers)
        self.assertEqual(response.status_code, 201)

        data = {'name': 'The Life of Bryant Collaguazo', 'year': 2018, 'gross': 100}
        response = self.app.post('/api/a/movies/',
                                 data=json.dumps(data),
                                 headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_post_invalid(self):
        """
        Test that invalid POST requests are processed correctly
        :return:
        """
        data = {'name': 'Bryant Collaguazo', 'age': 100, 'gross': 100}
        response = self.app.post('/api/a/actors/',
                                 data=json.dumps(data),
                                 headers={'Content-Type': 'not_json'})
        self.assertEqual(response.status_code, 400)

        data = {'age': 100, 'gross': 100}
        response = self.app.post('/api/a/actors/',
                                 data=json.dumps(data),
                                 headers=self.headers)
        self.assertEqual(response.status_code, 400)

        data = {'name': 'The Life of Bryant Collaguazo', 'year': 2018, 'gross': 100}
        response = self.app.post('/api/a/movies/',
                                 data=json.dumps(data),
                                 headers={'Content-Type': 'not_json'})
        self.assertEqual(response.status_code, 400)

        data = {'year': 2018, 'gross': 100}
        response = self.app.post('/api/a/movies/',
                                 data=json.dumps(data),
                                 headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_delete_valid(self):
        """
        Test that valid DELETE requests are processed correctly
        :return:
        """
        response = self.app.delete('/api/a/actors/Christopher Lloyd')
        self.assertEqual(response.status_code, 200)

        response = self.app.delete('/api/a/movies/Blind Date')
        self.assertEqual(response.status_code, 200)

    def test_delete_invalid(self):
        """
        Test that invalid DELETE requests are processed correctly
        :return:
        """
        response = self.app.delete('/api/a/actors/Bryant Collagauazo')
        self.assertEqual(response.status_code, 400)

        response = self.app.delete('/api/a/movies/The Life of Bryant Collaguazo')
        self.assertEqual(response.status_code, 400)
