import logging.config
import operator
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


class Query:
    def __init__(self, graph):
        self.graph = graph

    def get_gross(self, movie):
        """
        Retrieve the given movie's gross income
        :param movie: The movie whose gross income we want
        :return: The gross income of the movie
        """
        movie = self.graph.get_vertex(movie)

        if movie is not None:
            return movie.get_value1()

        return None

    def get_movies(self, actor):
        """
        Retrieve all the movies the given actor starred in
        :param actor: The actor the movies should have in it's cast
        :return: List of movies the acter starred in
        """

        if actor is None:
            return None

        movies = []
        actor_vertex = self.graph.get_vertex(actor)

        for movie in actor_vertex.get_neighbors():
            movies.append(movie)

        return movies

    def get_actors(self, movie):
        """
        Retrieve all the actors who starred in the specified movie
        :param movie: The movie the actors should have starred
        :return: List of actors who starred in the movie
        """
        movie_vertex = self.graph.get_vertex(movie)
        if movie is None:
            return None

        actors = []
        for actor in movie_vertex.get_neighbors():
            actors.append(actor)

        return actors

    def get_top_actors(self, num=10):
        """
        Retrieve the list of the num top grossing actors
        :param num: The specified number of actors to return, default 10
        :return: List of the top num grossing actors
        """
        actor_gross = {}

        for vertex in self.graph:
            if vertex.get_group() == "Actor":
                actor = vertex.get_key()
                movies = vertex.get_neighbors()
                total_gross = 0
                for movie in movies:
                    total_gross += vertex.get_weight(movie)
                actor_gross[actor] = total_gross

        sorted_actor_ages = sorted(actor_gross.items(), key=operator.itemgetter(1), reverse=True)
        top_actors = [(actor, gross) for (actor, gross) in sorted_actor_ages[:num]]

        return top_actors

    def get_oldest_actors(self, num=10):
        """
        Retrieve the list of the num oldest actors
        :param num: The specified number of actors to return, default 10
        :return: List of the top num oldest actors
        """
        actor_ages = {}

        for vertex in self.graph:
            if vertex.get_group() == "Actor":
                actor = vertex.get_key()
                age = vertex.get_value1()
                actor_ages[actor] = age

        sorted_actor_ages = sorted(actor_ages.items(), key=operator.itemgetter(1), reverse=True)
        oldest_actors = [(actor,age) for (actor,age) in sorted_actor_ages[:num]]

        return oldest_actors

    def get_movies_year(self, year):
        """
        Retrieve the movies who played in the given year
        :param year: The year the movie should have played
        :return: List of movies who meet the criteria
        """
        movies = []
        for vertex in self.graph:
            if vertex.get_group() == "Movie":
                movie_year = vertex.get_value2()
                if movie_year == year:
                    movies.append(vertex.get_key())

        return movies

    def get_actors_year(self, year):
        """
        Retrieve the actors who star in film in the given year
        :param year: The year the actor starred in the film
        :return: List of actors who meet the criteria
        """
        actors = {}
        movies = self.get_movies_year(year)
        for movie in movies:
            movie_actors = self.graph.get_vertex(movie).get_neighbors()
            for movie_actor in movie_actors:
                if movie_actor not in actors:
                    actors[movie_actor] = True

        return list(actors.keys())
