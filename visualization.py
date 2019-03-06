from pyvis.network import Network
import parse_data

COLOR_ACTOR = "#FF9AAB"
COLOR_MOVIE = "#B6BFA7"


class Visualization:
    def __init__(self, graph):
        self.graph = graph
        self.node_groups = []
        self.node_infos = []
        self.name_indices = {}
        self.net = Network(height="750px", width="100%")

    def visualize(self, file):
        """
        Visualize the graph and save it the given file
        :param file: The file for visualization of the graph
        :return: None
        """
        self.configure_graph()
        self.get_node_info()
        self.add_nodes()
        self.add_edges()

        self.net.show(file)

    def configure_graph(self):
        """
        Configure how the graph will be visualized
        :return: None
        """
        self.net.force_atlas_2based()
        self.net.show_buttons()
        self.net.toggle_stabilization(True)
        self.net.toggle_physics(True)

    def get_node_info(self):
        """
        Retrieve the attributes for all vertices(nodes) in the graph
        which will be displayed respective to each node
        :return: None
        """
        for index, vertex in enumerate(self.graph):
            group = vertex.get_group()
            self.node_groups.append(group)
            node_info = dict()
            node_info['Name'] = vertex.get_key()
            if group == 'Actor':
                node_info['Age'] = vertex.get_value1()
            else:
                node_info['Year'] = vertex.get_value1()
            self.node_infos.append(node_info)
            self.name_indices[vertex.get_key()] = index

    def get_titles(self):
        """
        Convert the attributes for each node into strings so
        they can be visualized
        :return:
        """
        titles = []
        for node_info in self.node_infos:
            title_info = " Info:<br>" + '<br/>'.join(['%s: %s' % (key, value) for (key, value) in node_info.items()])
            titles.append(title_info)
        return titles

    def add_nodes(self):
        """
        Add all nodes in our graph into the network graph object
        :return: None
        """
        titles = self.get_titles()
        self.net.add_nodes([index for index in range(len(titles))],
                           title=titles,
                           color=[COLOR_ACTOR if i == 'Actor' else COLOR_MOVIE for i in self.node_groups])

    def add_edges(self):
        """
        Add the edges in our graph into the network graph object
        :return: None
        """
        for vertex in self.graph:
            name = vertex.get_key()
            for neighbor in vertex.get_neighbors():
                self.net.add_edge(self.name_indices[name], self.name_indices[neighbor])


parse_graph = parse_data.parse('data.json')
visual = Visualization(parse_graph)
visual.visualize('visual.html')
