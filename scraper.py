from urllib.error import URLError, HTTPError
from urllib.request import urlopen
from bs4 import BeautifulSoup
from word2number import w2n
from decimal import Decimal
from random import randint
from time import sleep
from graph import Graph
from queue import Queue
from time import time
import logging.config
import yaml
import re


"""
Program: scraper.py
Author: Bryant Collaguazo

The purpose of this program is to scrape movie and actor
information from Wikipedia and store that data into a 
graph structure for queries.
"""

WIKI_URL = 'https://en.wikipedia.org'
MOVIE_THRESHOLD = 125
ACTOR_THRESHOLD = 250
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
            logger.info(f'{self.num_actors} actors found, {self.num_movies} movies found')

            # Continue on to the next url, if the given url is invalid
            if url is None:
                logger.debug(f'No {group} url given')
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
                group, url = self.scrape_handler(group, soup, url)
            else:
                logger.warning(f'Url:{url} is invalid')
                url, group = self.get_any_url(group)
                if url is None or group is None:
                    logger.warning(f'Ending scraper due to empty parameters, url:{url} group:{group}')
                    return
                continue

    def scrape_handler(self, group, soup, url):
        if group is ACTOR:
            self.scrape_actor(soup, url)
            url, group = (self.movie_queue.get(), MOVIE) if not self.movie_queue.empty() \
                else (self.actor_queue.get(), ACTOR)
        else:
            self.scrape_movie(soup, url)
            self.scrape_all_actors()
            url, group = (self.actor_queue.get(), ACTOR) if not self.actor_queue.empty() else \
                (self.movie_queue.get(), MOVIE)
        return group, url

    def scrape_all_actors(self):
        while not self.actor_queue.empty():
            url = self.actor_queue.get()

            # Try to get the raw web-page from the url
            # if error raise then continue to next url
            raw_page = open_url(url)
            if raw_page is not None:
                soup = BeautifulSoup(raw_page, 'html.parser')
                self.scrape_actor(soup, url)

    def get_any_url(self, group):
        logger.info(f'Exception occurred, current group: {group}')
        logger.info(f'Movie queue size {self.movie_queue.qsize()}')
        logger.info(f'Actor queue size {self.actor_queue.qsize()}')
        if group is ACTOR and not self.actor_queue.empty():
            return self.actor_queue.get(), group
        elif group is MOVIE and not self.movie_queue.empty():
            return self.movie_queue.get(), group
        else:
            return None, None

    def slow_scrape(self):
        #sleep(randint(1, 2))
        self.num_requests += 1
        elapsed_time = time() - self.start_time
        logger.info(f'Request Number:{self.num_requests} ;'
                    f'Request Frequency:{self.num_requests / elapsed_time} requests/sec')

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
        gross, title, year = get_movie_info(soup)
        if gross is not None and title is not None and year is not None:
            # Retrieve all the urls to the movie cast's Wikipedia page
            actor_urls = get_actor_urls(soup)
            self.add_movie(actor_urls, gross, title, url, year)
            if title in self.graph.get_vertices():
                for actor_url in actor_urls:
                    # Make sure not to add already scraped Wikipedia pages into our actor queue
                    if actor_url not in self.actor_urls:
                        self.actor_queue.put(actor_url)
                    # Otherwise, add an edge between the movie and actor
                    else:
                        self.add_movie_edge(actor_url, gross, title)

    def add_movie_edge(self, actor_url, gross, title):
        actor = self.actor_urls[actor_url]
        logger.info(f'Adding an edge between movie:{title} and actor:{actor}')
        actor_age = self.graph.get_vertex(actor).get_value1()
        weight = int(gross / actor_age)
        self.graph.add_edge(title, actor, weight)

    def add_movie(self, actor_urls, gross, title, url, year):
        # Add the movie into our graph if the graph doesn't already store it
        # and if we are able to find urls to the cast's Wikipedia pages
        if title not in self.graph.get_vertices() and actor_urls:
            # Store the url with the title of the movie it links to
            self.movie_urls[url] = title
            self.graph.add_vertex(MOVIE, title, gross, year)
            self.num_movies += 1

    def scrape_actor(self, soup, url):
        """
        Obtain the age and name from actor's web-page
        :param soup: The web-page to scrape
        :param url: The url of the web-page
        :return: None
        """
        logger.info(f'Actor url:{url}')
        age, name = get_actor_info(soup)
        if age is not None and name is not None:

            # Retrieve all the urls to the Wikipedia pages of the films the actor stars in
            movie_urls = get_movie_urls(soup)
            # Add the actor into our graph if the graph doesn't already store it
            # and if we are able to find urls to the films the actor stars in
            self.add_actor(age, movie_urls, name, url)
            if name in self.graph.get_vertices():
                for movie_url in movie_urls:
                    # Make sure not to add already scraped Wikipedia pages into our movie queue
                    if movie_url not in self.movie_urls:
                        self.movie_queue.put(movie_url)
                    # Otherwise, add an edge between the actor and movie
                    else:
                        self.add_actor_edge(age, movie_url, name)

    def add_actor(self, age, movie_urls, name, url):
        if name not in self.graph.get_vertices() and movie_urls:
            # Store the url with the name of the actor it links to
            self.actor_urls[url] = name
            self.graph.add_vertex(ACTOR, name, age)
            self.num_actors += 1

    def add_actor_edge(self, age, movie_url, name):
        movie = self.movie_urls[movie_url]
        movie_gross = self.graph.get_vertex(movie).get_value1()
        weight = int(movie_gross / age)
        self.graph.add_edge(name, movie, weight)

    def get_graph(self):
        return self.graph


def get_actor_info(soup):
    """
    Obtain the actor information, age and name, from the web-page
    :param soup: The raw html representation of the Wikipedia page
    :return: The age and name of found actor, if available
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
        age = int(re.sub('[^0-9]', '', age))

    logger.debug(f'Found actor name:{name}, age:{age}')
    return age, name


def get_movie_info(soup):
    """
    Obtain the movie information, gross income, title,
    and release date from the web-page
    :param soup: The raw html representation of the Wikipedia page
    :return: The gross income, title, and release date, if available
    """

    logger.info("Retrieving movie information from web-page")
    gross = None
    title = None

    title_box = soup.find('h1', attrs={'class': 'firstHeading'})
    gross_box = get_movie_gross(soup)

    title = strip_tags(title, title_box)
    gross = strip_tags(gross, gross_box)
    year = get_movie_year(soup)
    logger.info(f'Year found: {year}')

    if title is None or gross is None or year is None:
        logger.warning("Not able to get movie information")
    else:
        gross = parse_gross(gross)

    logger.debug(f'Found movie title:{title}, gross:{gross}')
    return gross, title, year


def get_movie_gross(soup):
    """
    Obtain the gross income from the movie's Wikipedia page
    :param soup: The raw html representation of the Wikipedia page
    :return: The element holding the gross income, if any
    """
    ths = soup.find_all('th')
    for th in ths:
        if th.text == "Box office":
            return th.next_sibling
    return None


def get_movie_year(soup):
    """
    Obtain the release date of a movie from it's Wikipedia page
    :param soup: The raw html representation of the Wikipedia page
    :return: The year the movie was released, if available
    """
    year = None

    ths = soup.find_all('th')
    for th in ths:
        if th.text == "Release date" and th.next_sibling is not None:
            div = th.next_sibling
            ul = div.find('ul')
            if ul is not None and ul.next_element is not None:
                li = ul.next_element
                text = re.findall('[0-9]{4}', li.text)
                if text:
                    year = int(text[0])
            return year

    return year


def get_movie_urls(soup):
    """
    Obtain all the movie urls on the actor's Wikipedia page
    :param soup: The raw html representation of the Wikipedia page
    :return: Any movie urls found in the page
    """
    url_links = get_movie_urls_div(soup)

    if not url_links:
        url_links = get_movie_urls_wikitable(soup)

    return url_links


def get_movie_urls_div(soup):
    """
    Obtain movie urls from a actor Wikipedia, if they are inside div elements
    :param soup: The web-page to be searched
    :return: Any urls found
    """

    logger.info(f'Retrieving urls by searching divs')
    url_links = []

    data = soup.findAll('div', attrs={'class': 'div-col columns column-width'})

    for div in data:
        links = div.findAll('a')
        for a in links:
            url_links.append(WIKI_URL + a['href'])

    logger.info(f'Found {len(url_links)} url links by searching divs')
    return url_links


def get_movie_urls_wikitable(soup):
    """
    Obtain movie urls from a actor Wikipedia, if they are inside a wikitable element
    :param soup: The raw html representation of the Wikipedia page
    :return: Any movie urls found in the page
    """
    logger.info(f'Retrieving urls by searching wikitable')

    span = soup.find('span', attrs={'class': 'mw-headline', 'id': 'Film'})

    url_links = []
    if span is not None:
        h3 = span.parent
        table = h3.find_next('table')
        if table is not None and table['class'][0] == 'wikitable':
            for row in table.find_all('tr'):
                tds = row.find_all('td')
                for td in tds:
                    a = td.find('a')
                    if a is not None:
                        url_links.append(WIKI_URL + a['href'])

    logger.info(f'Found {len(url_links)} url links by searching wikitable')
    return url_links


def get_actor_urls(soup):
    """
    Obtain all the actor urls on the movies's Wikipedia page
    :param soup: The raw html representation of the Wikipedia page
    :return: Any actor urls found in the page
    """
    logger.info(f'Retrieving actor urls')
    url_links = []

    for t in soup.findAll(text='Starring'):
        logger.info(f'{t}')
        p = t.parent
        if p.name != 'th':
            continue
        ns = p.nextSibling
        logger.info(f'{ns}')
        if not ns or ns.name not in ['td']:
            continue
        links = ns.findAll('a')
        for a in links:
            url = WIKI_URL + a['href']
            url_links.append(url)
            logger.debug(f'Found Actor url: {url}')

    logger.info(f'Found {len(url_links)} actor url links')

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


def parse_gross(gross_string):
    """
    Parse gross income string into integer
    :param gross_string: String to be parsed
    :return: Integer representation of the gross income string
    """
    logger.info(f'Parsing gross income string')
    gross_string = remove_paren_brack(gross_string)
    gross_string = remove_non_alphanum(gross_string)
    nums_in_gross = re.findall('\\d*\\.?\\d+', gross_string)

    logger.debug(f'Alphanumeric Gross: {gross_string}')
    logger.debug(f'Numbers found in Gross: {nums_in_gross}')

    try:
        magnitude = Decimal(w2n.word_to_num(gross_string))
    except ValueError as e:
        logger.warning(e)
        magnitude = Decimal(1)
        pass

    gross_num = Decimal(nums_in_gross[0])
    logger.debug(f'Gross digits {gross_num}')
    logger.debug(f'Gross magnitude: {magnitude}')

    gross = None
    if not magnitude == gross_num:
        gross = int(gross_num * magnitude)
    else:
        gross = int(gross_num)

    logger.debug(f'Gross income: {gross}')
    return gross


def remove_paren_brack(string):
    """
    Remove parentheses and bracket content in s
    :param string: String to be parsed
    :return: Parsed string with parentheses and bracket content removed
    """
    string = re.sub(r'\([^)]*\)', '', string)
    string = re.sub(r'\[[^)]*\]', '', string)
    return string


def remove_non_alphanum(string):
    """
    Remove all non-alphanumeric characters and non-float numbers
    :param string: The string to be parsed
    :return: Alphanumeric represenation of the input string
    """
    logger.info(f'Removing non-alphanumeric characters')
    ret = re.sub(r'[^\w\s(?<!\d)\.(?<!\d)]', '', string)

    return ret


def open_url(url):
    """
    Obtain the raw web-page from the given url
    :param url: The url to be opened
    :return: The raw web-page, if no error raised
    """
    raw_page = None

    logger.info(f'Accessing {url}')
    try:
        raw_page = urlopen(url)
    except HTTPError as e:
        logger.warning(f'HTTPError:{e.code}, url:{url}')
    except URLError as e:
        logger.warning(f'URLError:{e.errno}, url:{url}')
    else:
        logger.info(f'Successful connection:{url}')

    return raw_page
