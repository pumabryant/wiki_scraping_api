from utils import load, save, parse, analyze_plot
from query import Query
from analyze import Analyze
from scraper import Scraper

URL = "https://en.wikipedia.org/wiki/Morgan_Freeman"
TYPE = "Actor"


def main():
    scraper = Scraper()
    scraper.scrape(URL, TYPE)
    save("scraper_data.json", scraper.get_graph())


def load_query():
    graph = load('scraper_data.json')
    query = Query(graph)
    query_year = 2008
    query_gross_movie = "The Dark Knight (film)"
    query_movie = "Now You See Me 2"
    query_actor = "Dave Franco"

    print(f'Gross Income for {query_gross_movie}: {query.get_gross(query_gross_movie)}')
    print(f'Actors in {query_movie}: {query.get_actors(query_movie)}')
    print(f'Movies starring {query_actor}: {query.get_movies(query_actor)}')
    print(f'Movies in {query_year}: {query.get_movies_year(query_year)}')
    print(f'Actors in {query_year}: {query.get_actors_year(query_year)}')
    print(f'Oldest Actors: {query.get_oldest_actors()}')
    print(f'Top Grossing Actors: {query.get_top_actors()}')


def part2():
    graph = parse('data.json')
    analyzer = Analyze(graph)
    actor_connections, num = analyzer.get_hub_actors()
    age_gross, num = analyzer.get_gross_age()
    analyze_plot(actor_connections, num, xlabel='Actors',
                 ylabel='Num of Connections', title='Connections per Actor')
    analyze_plot(age_gross, num, xlabel='Age',
                 ylabel='Total Gross', title='Total Gross per Age')


part2()
