import re
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from random import randint
from time import sleep
from time import time
from queue import Queue
from graph import Graph
import logging.config
import yaml


"""
Program: scraper.py
Author: Bryant Collaguazo

The purpose of this program is to scrape movie and actor
information from Wikipedia and store that data into a 
graph structure for queries.
"""

MOVIE_THRESHOLD = 10
ACTOR_THRESHOLD = 10
ACTOR = "Actor"
MOVIE = "Movie"

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self):
        """
        Initialize the Scraper object
        """
        self.num_requests = 0
        self.num_movies = 0
        self.num_actors = 0
        self.graph = Graph()
        self.start_time = time()
        self.movie_queue = Queue()
        self.actor_queue = Queue()
        self.movie_urls = {}
        self.actor_urls = {}

    def scrape(self, url, group=None):
        """
        Dynamically scrape information from Wikipedia till
        a certain threshold has been met
        :param url: The url to start scraping from
        :param group: The type of the page the url is linking to
        :return: None
        """

        while self.num_movies < MOVIE_THRESHOLD or self.num_actors < ACTOR_THRESHOLD:
            # Continue on to the next url, if the given url is invalid
            if url is None:
                # TODO
                logger.debug(f'Not a valid {group} url')
                url, group = self.get_any_url(group)
                continue

            # Stop scraping after we have retrieve enough movie and actor information
            if self.num_movies >= MOVIE_THRESHOLD and self.num_actors >= ACTOR_THRESHOLD:
                logger.info(f'Scraped {self.num_movies} movie and {self.num_actors} actor pages')
                break

            # Slow web-scraper down
            self.slow_scrape()

            # Try to get the raw web-page from the url
            # if error raise then continue to next url
            raw_page = open_url(url)
            if raw_page is not None:
                soup = BeautifulSoup(raw_page, 'html.parser')
                if group is ACTOR:
                    self.scrape_actor(soup, url)
                    url = self.movie_queue.get() if not self.movie_queue.empty() else self.actor_queue.get()
                    group = MOVIE
                else:
                    self.scrape_movie(soup, url)
                    url = self.actor_queue.get() if not self.actor_queue.empty() else self.movie_queue.get()
                    group = ACTOR
            else:
                url, group = self.get_any_url(group)
                continue

    def get_any_url(self, group):
        if group == ACTOR and not self.movie_queue.empty():
            return self.movie_queue.get(), MOVIE
        elif group == MOVIE and not self.actor_queue.empty():
            return self.actor_queue.get(), ACTOR
        else:
            return None

    def slow_scrape(self):
        sleep(randint(1, 2))
        self.num_requests += 1
        elapsed_time = time() - self.start_time
        logger.info(f'Request:{self.num_requests}; Frequency:{self.num_requests / elapsed_time} requests/sec')

    def scrape_movie(self, soup, url):
        """
        Obtain the gross income and title from movie's web-page
        :param soup: The web-page to scrape
        :param url: The url of the web-page
        :return: None
        """
        # Check if we've already processed this url before
        if url in self.movie_urls:
            return
        gross, title = get_movie(soup)
        if gross is not None and title is not None:
            # Store the url with the title of the movie it links to
            self.movie_urls[url] = title
            # Add the movie into our graph if the graph doesn't already store it
            if title not in self.graph.get_vertices():
                self.graph.add_vertex(title, gross, MOVIE)
                vertex = self.graph.get_vertex(title)
                logger.info(f'Key:{vertex.get_key()}, Value:{vertex.get_value()}m Group:{vertex.get_group()}')
                self.num_movies += 1
            # Retrieve all the urls to the movie cast's Wikipedia page
            for actor_url in get_urls(soup):
                # Make sure not to add already scraped Wikipedia pages into our actor queue
                if actor_url not in self.actor_urls:
                    self.actor_queue.put(actor_url)
                # Otherwise, add an edge between the movie and actor
                else:
                    actor = self.actor_urls[actor_url]
                    logger.info(f'Adding edge between {title} and {actor}')
                    self.graph.add_edge(title, actor, 1)

    def scrape_actor(self, soup, url):
        """
        Obtain the age and name from actor's web-page
        :param soup: The web-page to scrape
        :param url: The url of the web-page
        :return: None
        """
        age, name = get_actor(soup)
        if age is not None and name is not None:
            # Store the url with the name of the actor it links to
            self.actor_urls[url] = name
            # Add the actor into our graph if the graph doesn't already store it
            if name not in self.graph.get_vertices():
                self.graph.add_vertex(name, age, ACTOR)
                self.num_actors += 1

            # Retrieve all the urls to the Wikipedia pages of the films the actor stars in
            for movie_url in get_urls(soup):
                # Make sure not to add already scraped Wikipedia pages into our movie queue
                if movie_url not in self.movie_urls:
                    self.movie_queue.put(movie_url)
                    gross, title
                # Otherwise, add an edge between the actor and movie
                else:
                    movie = self.movie_urls[movie_url]
                    self.graph.add_edge(name, movie, 1)

    def get_graph(self):
        return self.graph


WIKI_URL = 'https://en.wikipedia.org'


def get_actor(soup):
    """
    Retrieve actor information from the web-page, if possible
    :param soup: The webpage to be searched
    :return: The age and name of found actor, if any
    """
    logger.info('Retrieving actor information from web-page')
    name = None
    age = None

    name_box = soup.find('h1', attrs={'class': 'firstHeading'})
    age_box = soup.find('span', attrs={'class': 'noprint ForceAgeToShow'})

    name = strip_tags(name, name_box)
    age = strip_tags(age, age_box)

    if name is None or age is None:
        logger.warning("Not able to get actor information")
    else:
        age = re.sub('[^0-9]', '', age)

    logger.debug(f'name:{name}, age:{age}')
    return age, name


def get_movie(soup):
    """
    Retrieve the movie information from the web-page, if possible
    :param soup: The webpage to be searched
    :return: The gross income and title of found movie, if any
    """

    logger.info("Retrieving movie information from web-page")
    gross = None
    title = None

    title_box = soup.find('h1', attrs={'class': 'firstHeading'})
    gross_box = get_gross(soup)

    title = strip_tags(title, title_box)
    gross = strip_tags(gross, gross_box)

    if title is None or gross is None:
        logger.warning("Not able to get movie information")

    logger.debug(f'title:{title}, gross:{gross}')
    return gross, title


def get_gross(soup):
    """
    Get the gross income from the movie's webpage, if possible
    :param soup: The web-page to be searched
    :return: The element holding the gross income, if any
    """
    ths = soup.find_all('th')
    for th in ths:
        if th.text == "Box office":
            return th.next_sibling
    return None


def get_urls(soup):
    """
    Retrieve the urls from the web-page
    :param soup: The web-page to be searched
    :return: Any urls found
    """

    logger.info(f'Retrieving urls')
    url_links = []

    data = soup.findAll('div', attrs={'class': 'div-col columns column-width'})

    for div in data:
        links = div.findAll('a')
        for a in links:
            url_links.append(WIKI_URL + a['href'])

    return url_links


def strip_tags(var, box):
    """
    Get rid of the HTML tags and obtain just the text
    :param var: Variable to store text
    :param box: Tag box to be stripped down
    :return: Updated variable state
    """
    logger.info("Stripping away HTML tags")
    if box is not None:
        var = box.text.strip()
    return var


def open_url(url):
    """
    Obtain the raw web-page from the given url
    :param url: The url to be opened
    :return: The raw web-page, if no error raised
    """
    raw_page = None

    try:
        raw_page = urlopen(url)
    except HTTPError as e:
        logger.warning(f'HTTPError:{e.code}')
    except URLError as e:
        logger.warning(f'URLError:{e.errno}')
    else:
        logger.info("Successful connection")

    return raw_page
