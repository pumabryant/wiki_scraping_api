from utils import get_actor_num_connections, get_coactor_count


class Analyze:
    def __init__(self, graph):
        self.graph = graph

    def get_hub_actors(self, num=10):
        """
        Get a hub of num actors with the most connections to other actors
        :param num: The number of actors to display
        :return: The dictionary actor/connection values and the number of actors
        """
        actor_connections = {}

        for vertex in self.graph:
            if vertex.get_group() == "Movie":
                actors = vertex.get_neighbors()
                get_coactor_count(actor_connections, actors)

        actor_num_connections = {}
        get_actor_num_connections(actor_connections, actor_num_connections)

        return actor_num_connections, num

    def get_gross_age(self, num=10):
        """
        Get the total gross for all ages and display the top num age groups
        :param num: The number of age groups to display
        :return: The dictionary age/gross values and the number of of age groups
        """
        age_gross = {}

        for vertex in self.graph:
            if vertex.get_group() == "Movie":
                actors = vertex.get_neighbors()
                for actor in actors:
                    info = self.graph.get_vertex(actor)
                    age = info.get_value1()
                    gross = info.get_value2()
                    if age not in age_gross:
                        age_gross[age] = gross
                    else:
                        age_gross[age] += gross

        return age_gross, num
