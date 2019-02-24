from collections import OrderedDict

class Vertex:
    def __init__(self, key, value, group):
        self.key = key
        self.value = value
        self.group = group
        self.neighbors = OrderedDict()

    def add_neighbor(self, neighbor, weight):
        self.neighbors[neighbor] = weight

    def get_neighbors(self):
        return self.neighbors

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value

    def get_group(self):
        return self.group

    def get_weight(self, neighbor):
        return self.neighbors[neighbor]
