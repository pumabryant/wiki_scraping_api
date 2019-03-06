from graph import Graph
from utils import *


def parse(filename):
    """
    Parse the data in 'filename' to our graph data_structure
    :param filename: The JSON file to load
    :return: The graph representation of the data from the JSON file
    """
    graph = Graph()
    actor_data = load(filename)[0]
    movie_data = load(filename)[1]

    for key, value in actor_data.items():
        age, group, movies, name, total_gross = value.values()
        graph.add_vertex(group, key, age, total_gross)

    for key, value in movie_data.items():
        actors, gross, group, title, url, year = value.values()
        graph.add_vertex(group, key, year, gross)
        for actor in actors:
            if actor in graph.get_vertices():
                graph.add_edge(title, actor, 1)

    return graph
