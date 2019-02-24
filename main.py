from utils import load, save
from query import Query
from scraper import Scraper

def main():

    scraper = Scraper()
    query = Query(scraper.get_graph())
    scraper.scrape("https://en.wikipedia.org/wiki/Morgan_Freeman", "Actor")

    movies = query.get_movies("Morgan Freeman")
    for movie in movies:
        print(movie)

    save("data.json", scraper.get_graph())

def try_load():
    graph = load('data.json')
    query = Query(graph)
    movies = query.get_movies("Morgan Freeman")
    actors = query.get_actors("Brubaker")
    for movie in movies:
        print(movie)
    for actor in actors:
        print(actor)


#main()
try_load()