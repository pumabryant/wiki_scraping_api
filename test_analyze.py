import unittest
from utils import parse
from analyze import Analyze


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.graph = parse('data.json')
        self.analyzer = Analyze(self.graph)

    def test_outcome(self):
        actor_connections, num = self.analyzer.get_hub_actors()
        self.assertEqual(num, 10)
        age_gross, num = self.analyzer.get_gross_age()
        self.assertEqual(num, 10)
