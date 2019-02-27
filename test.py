import unittest


class GraphTestCase(unittest.TestCase):
    def test_add_vertex(self):
        """
        Check if adding a vertex works
        :return: None
        """
        from graph import Graph
        g = Graph()
        g.add_vertex("Student", "Bryant Collaguazo", 21)
        v = g.get_vertex("Bryant Collaguazo")
        self.assertNotEqual(v, None)

    def test_add_edge(self):
        """
        Check if edges are created between vertices
        :return: None
        """
        from graph import Graph
        g = Graph()
        g.add_vertex("Student", "Bryant Collaguazo", 21)
        g.add_vertex("Worker", "Edward Collaguazo", 23)
        g.add_edge("Bryant Collaguazo", "Edward Collaguazo", 1)
        v = g.get_vertex("Bryant Collaguazo")
        self.assertEqual(v.get_weight("Edward Collaguazo"), 1)

    def test_get_vertices(self):
        """
        Check whether vertices are being properly stored and returned
        :return: None
        """
        from graph import Graph
        g = Graph()
        g.add_vertex("Student", "Bryant Collaguazo", 21)
        g.add_vertex("Worker", "Edward Collaguazo", 23)
        g.add_edge("Bryant Collaguazo", "Edward Collaguazo", 1)
        v = g.get_vertices()
        self.assertEqual(len(v), 2)

    def test_iter_graph(self):
        """
        Check if we can iterate through the graph's vertices
        :return: None
        """
        from graph import Graph
        from vertex import Vertex
        g = Graph()
        g.add_vertex("Student", "Bryant Collaguazo", 21)
        g.add_vertex("Worker", "Edward Collaguazo", 23)
        g.add_edge("Bryant Collaguazo", "Edward Collaguazo", 1)
        for v in g:
            self.assertEqual(type(v), Vertex)


class VertexTestCase(unittest.TestCase):
    def test_get_attributes(self):
        """
        Check if attributes are being properly stored inside the vertex
        :return: None
        """
        from vertex import Vertex
        v = Vertex("Student", "Bryant Collaguazo", 21, 2019)

        self.assertEqual(v.get_group(), "Student")
        self.assertEqual(v.get_key(), "Bryant Collaguazo")
        self.assertEqual(v.get_value1(), 21)
        self.assertEqual(v.get_value2(), 2019)

    def test_add_get_neighbor(self):
        """
        Check if neighbor vertices are being properly stored and returned
        :return: None
        """
        from vertex import Vertex
        v = Vertex("Student", "Bryant Collaguazo", 21, 1)
        v.add_neighbor("Edward Collaguazo", 1)
        neighbors = v.get_neighbors()

        self.assertEqual("Edward Collaguazo" in neighbors, True)


class QueryTestCase(unittest.TestCase):
    def test_get_gross(self):
        from graph import Graph
        from query import Query
        g = Graph()
        q = Query(g)
        g.add_vertex("Movie", "Avengers: Infinity War", 2048000000)

        self.assertEqual(q.get_gross("Avengers: Infinity War"), 2048000000)
        self.assertEqual(q.get_gross("Untitled Movie"), None)

    def test_get_movies(self):
        from graph import Graph
        from query import Query
        g = Graph()
        q = Query(g)
        g.add_vertex("Movie", "Avengers: Infinity War", 2048000000)
        g.add_vertex("Movie", "Iron Man", 1048000000)
        g.add_vertex("Actor", "Robert Downey Jr.", 53)
        g.add_edge("Avengers: Infinity War", "Robert Downey Jr.", 2048000000)
        g.add_edge("Iron Man", "Robert Downey Jr.", 1048000000)

        movies = q.get_movies("Robert Downey Jr.")

        self.assertEqual("Avengers: Infinity War" in movies, True)
        self.assertEqual("Iron Man" in movies, True)
