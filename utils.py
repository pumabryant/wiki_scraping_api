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
                age = graph.get_vertex(actor).get_value1()
                graph.add_edge(title, actor, gross/age)

    return graph


def analyze_plot(data_dict, num, xlabel="", ylabel="", title=""):
    """
    Plot the given dictionary of key-value pairs in a bar chart
    :param data_dict: Dictionary that holds the data to be plotted
    :param num: The number of data points to plot
    :param xlabel: The X-axis label
    :param ylabel: The Y-axis label
    :param title: The plot's title
    :return:
    """
    data_dict = dict(sorted(data_dict.items(), key=operator.itemgetter(1), reverse=True))
    x = list(data_dict.keys())
    y = list(data_dict.values())
    plt.bar(x[:num], y[:num])
    plt.xticks(rotation=90)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def get_actor_num_connections(actor_connections, actor_num_connections):
    """
    Get the total number of connections an actor has in a graph
    :param actor_connections: The dictionary to store the connections information
    :param actor_num_connections: The dictionary that holds the actor and coactor counts
    :return:
    """
    for actor, co_actors in actor_connections.items():
        actor_num_connections[actor] = 0
        for _, connections in co_actors.items():
            actor_num_connections[actor] += connections


def get_coactor_count(actor_connections, actors):
    """
    Get the number of times an actor and another actor star in the same movie
    :param actor_connections: The dictionary that holds the count information
    :param actors: The actors to be analyzed
    :return:
    """
    for actor in actors:
        if actor not in actor_connections:
            actor_connections[actor] = {}
        for co_actor in actors:
            if co_actor != actor:
                if co_actor not in actor_connections[actor]:
                    actor_connections[actor][co_actor] = 1
                else:
                    actor_connections[actor][co_actor] += 1