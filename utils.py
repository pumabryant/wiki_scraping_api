import logging.config

import jsonpickle
import yaml


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
