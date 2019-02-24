from vertex import Vertex
from collections import OrderedDict


class Graph:
    def __init__(self):
        self.vertices = OrderedDict()
        self.numVertices = 0

    def add_vertex(self, key, value, group):
        self.numVertices += 1
        vertex = Vertex(key, value, group)
        self.vertices[key] = vertex
        return vertex

    def get_vertex(self, key):
        return self.vertices[key] if key in self.vertices else None

    def add_edge(self, key1, key2, weight):
        if key1 not in self.vertices:
            self.add_vertex(key1)
        if key2 not in self.vertices:
            self.add_vertex(key2)

        self.vertices[key1].add_neighbor(self.vertices[key2], weight)
        self.vertices[key2].add_neighbor(self.vertices[key1], weight)

    def get_vertices(self):
        return self.vertices.keys()

    def __iter__(self):
        return iter(self.vertices.values())
