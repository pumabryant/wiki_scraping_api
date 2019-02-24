import logging.config
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


class Query:
    def __init__(self, graph):
        self.graph = graph
        self.gross = {}
        self.oldest = {}

    def get_gross(self, movie):
        """
        Retrieve the given movie's gross income
        :param movie: The movie whose gross income we want
        :return: The gross income of the movie
        """
        movie = self.graph.get_vertex(movie)
        if movie is None:
            return None
        return movie.get_value()

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
            movies.append(movie.get_key())

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
            actors.append(actor.get_key())

        return actors

    def get_top_actors(self, num=10):
        """
        Retrieve the list of the num top grossing actors
        :param num: The specified number of actors to return, default 10
        :return: List of the top num grossing actors
        """
        for vertex in self.graph:
            if vertex.get_group() is "Actor":
                actor = vertex.get_key()
                movies = vertex.get_neighbors()
                total_gross = 0
                for movie in movies:
                    total_gross += vertex.get_weight(movie)
                self.gross[actor] = total_gross

        return self.gross

    def get_oldest_actors(self, num=10):
        """
        Retrieve the list of the num oldest actors
        :param num: The specified number of actors to return, default 10
        :return: List of the top num oldest actors
        """
        for vertex in self.graph:
            if vertex.get_group() is "Actor":
                actor = vertex.get_key()
                age = vertex.get_value()
                self.oldest[actor] = age

        return self.oldest

    def get_movies_year(self, year):
        """
        Retrieve the movies who played in the given year
        :param year: The year the movie should have played
        :return: List of movies who meet the criteria
        """
        movies = []
        for vertex in self.graph.get_vertices():
            if vertex.get_group() is "Movie":
                movie_title = vertex.get_key()
                movie_year = vertex.get_value()
                if movie_year == year:
                    movies.append(movie_title)

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
            movie_actors = movie.get_neighbors()
            for movie_actor in movie_actors:
                if movie_actor not in actors:
                    actors[movie_actor] = True

        return actors.keys()
