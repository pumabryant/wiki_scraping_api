import logging.config
import operator

import jsonpickle
import yaml
from matplotlib import pyplot as plt

from graph import Graph

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def save(filename, obj):
    """
    Save data in a JSON for future use
    :param filename: The name of the destination file
    :param obj: The object to be saved
    :return: None
    """
    logger.info("Saving data into file")
    if filename is None:
        logger.warning("Invalid filename")
        return

    jsonpickle.set_encoder_options('json', indent=4)
    data = jsonpickle.encode(obj)
    with open(filename, 'w+') as save_file:
        print(data, file=save_file)


def load(filename):
    """
    Load in previously saved data, if possible, from JSON file
    :param filename: The JSON file to load
    :return: The object represented from the data in the JSON file
    """
    logger.info('Loading in data from JSON file')
    with open(filename, "r") as save_file:
        data = jsonpickle.decode(save_file.read())

    return data


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


def analyze_plot(data_dict, num):
    data_dict = dict(sorted(data_dict.items(), key=operator.itemgetter(1), reverse=True))
    x = list(data_dict.keys())
    y = list(data_dict.values())
    plt.bar(x[:num], y[:num])
    plt.xticks(rotation=90)
    plt.show()


def get_actor_num_connections(actor_connections, actor_num_connections):
    for actor, co_actors in actor_connections.items():
        actor_num_connections[actor] = 0
        for _, connections in co_actors.items():
            actor_num_connections[actor] += connections


def get_coactor_count(actor_connections, actors):
    for actor in actors:
        if actor not in actor_connections:
            actor_connections[actor] = {}
        for co_actor in actors:
            if co_actor != actor:
                if co_actor not in actor_connections[actor]:
                    actor_connections[actor][co_actor] = 1
                else:
                    actor_connections[actor][co_actor] += 1