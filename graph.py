from vertex import Vertex


class Graph:
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, group, key, value1, value2=-1):
        vertex = Vertex(group, key, value1, value2)
        self.vertices[key] = vertex
        return vertex

    def delete_vertex(self, key):
        del self.vertices[key]

    def get_vertex(self, key):
        return self.vertices[key] if key in self.vertices else None

    def add_edge(self, key1, key2, weight):
        self.vertices[key1].add_neighbor(key2, weight)
        self.vertices[key2].add_neighbor(key1, weight)

    def get_vertices(self):
        return self.vertices.keys()

    def __iter__(self):
        return iter(self.vertices.values())
