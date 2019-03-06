

class Vertex:
    def __init__(self, group, key, value1, value2):
        self.group = group
        self.key = key
        self.value1 = value1
        self.value2 = value2
        self.neighbors = {}

    def add_neighbor(self, neighbor, weight):
        self.neighbors[neighbor] = weight

    def get_neighbors(self):
        return self.neighbors

    def get_key(self):
        return self.key

    def set_key(self, key):
        self.key = key

    def get_value1(self):
        return self.value1

    def set_value1(self, value1):
        self.value1 = value1

    def get_value2(self):
        return self.value2

    def set_value2(self, value2):
        self.value2 = value2

    def get_group(self):
        return self.group

    def get_weight(self, neighbor):
        return self.neighbors[neighbor]
