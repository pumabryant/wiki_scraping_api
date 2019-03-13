from flask import Flask, jsonify, request, make_response, abort
import utils

app = Flask(__name__)

graph = utils.parse('data.json')


""" GET METHODS """


@app.route('/actors', methods=['GET'])
def get_filtered_actors():
    """
    Filter out actors who do not match some chosen attributes
    :return:
    """
    filter_names = request.args.getlist('name')
    filter_ages = request.args.getlist('age', type=int)
    filter_gross = request.args.getlist('gross', type=int)

    actors = {}
    for vertex in graph:
        name = vertex.get_key()
        age = vertex.get_value1()
        gross = vertex.get_value2()
        if vertex.get_group() == 'Actor' and \
                does_match_filters(name, age, gross, filter_names, filter_ages, filter_gross):
            actor = dict()
            actor['name'] = name
            actor['age'] = age
            actor['gross'] = gross
            actors[vertex.get_key()] = actor

    if not actors:
        abort(400)

    return jsonify(actors)


@app.route('/movies', methods=['GET'])
def get_filtered_movies():
    """
    Filter out movies who do not match some chosen attributes
    :return:
    """
    filter_names = request.args.getlist('name')
    filter_gross = request.args.getlist('gross', type=int)
    filter_years = request.args.getlist('year', type=int)

    movies = {}
    for vertex in graph:
        title = vertex.get_key()
        gross = vertex.get_value1()
        year = vertex.get_value2()
        if vertex.get_group() == 'Movie' and \
                does_match_filters(title, gross, year, filter_names, filter_years, filter_gross):
            movie = dict()
            movie['name'] = title
            movie['gross'] = gross
            movie['year'] = year
            movies[vertex.get_key()] = movie

    if not movies:
        abort(400)

    return jsonify(movies)


def does_match_filters(name, value_1, value_2, filter_names, filter_value1, filter_value2):
    """
    Determine if the given attributes match any of the selected filters
    :param name: The name of the movie/actor
    :param value_1: The age/year of the movie/actor
    :param value_2: The gross of the movie/actor
    :param filter_names: The movies/actors to be filtered
    :param filter_value1: The ages/years to be filtered
    :param filter_value2: The gross' to be filtered
    :return: If the attributes match the filters
    """
    match_name = False
    match_value_1 = False
    match_value_2 = False

    for filter_name in filter_names:
        if filter_name in name:
            match_name = True
            break

    if value_1 in filter_value1:
        match_value_1 = True

    if value_2 in filter_value2:
        match_value_1 = True

    return match_name or match_value_1 or match_value_2


@app.route('/actors/<actor_name>', methods=['GET'])
def get_actor(actor_name):
    """
    Retrive the first actor meta-info who matches with the given actor name
    :return:
    """
    actor_meta = {}
    for vertex in graph:
        if vertex.get_group() == 'Actor' and vertex.get_key() == actor_name:
            actor = dict()
            actor['name'] = vertex.get_key()
            actor['age'] = vertex.get_value1()
            actor['gross'] = vertex.get_value2()
            actor_meta[actor_name] = actor

    if not actor_meta:
        abort(404)

    return jsonify(actor_meta)


@app.route('/movies/<movie_title>', methods=['GET'])
def get_movie(movie_title):
    """
    Retrive the first movie meta-info who matches with the given movie name
    :return:
    """
    movie_meta = {}
    for vertex in graph:
        if vertex.get_group() == 'Movie' and vertex.get_key() == movie_title:
            movie = dict()
            movie['title'] = vertex.get_key()
            movie['year'] = vertex.get_value1()
            movie['gross'] = vertex.get_value2()
            movie_meta[movie_title] = movie

    if not movie_meta:
        abort(404)

    return jsonify(movie_meta)


""" PUT METHODS """


@app.route('/api/a/actors/<string:actor_name>', methods=['PUT'])
def update_actor(actor_name):
    """
    Update the given actor's meta-info, if valid
    :param actor_name: The name of the actor whose meta-info should be updated
    :return:
    """
    if actor_name not in graph.get_vertices():
        abort(404)
    if not request.json:
        abort(400)

    actor_meta = graph.get_vertex(actor_name)

    age = request.json.get('age', actor_meta.get_value1())
    actor_meta.set_value1(age)

    gross = request.json.get('gross', actor_meta.get_value2())
    actor_meta.set_value2(gross)

    actor = dict()
    actor['name'] = actor_name
    actor['age'] = age
    actor['gross'] = gross

    return jsonify(actor)


@app.route('/api/a/movies/<string:movie_name>', methods=['PUT'])
def update_movie(movie_name):
    """
    Update the given movies's meta-info, if valid
    :param movie_name: The name of the movie whose meta-info should be updated
    :return:
    """
    if movie_name not in graph.get_vertices():
        abort(404)
    if not request.json:
        abort(400)

    movie_meta = graph.get_vertex(movie_name)

    year = request.json.get('year', movie_meta.get_value1())
    movie_meta.set_value1(year)

    gross = request.json.get('gross', movie_meta.get_value2())
    movie_meta.set_value2(gross)

    movie = dict()
    movie['title'] = movie_name
    movie['year'] = year
    movie['gross'] = gross

    return jsonify(movie)


""" POST METHODS """


@app.route('/api/a/actors/', methods=['POST'])
def create_actor():
    """
    Create an actor object with given attributes, if valid
    :return:
    """
    if not request.json or 'name' not in request.json:
        abort(400)

    name = request.json['name']
    age = request.json.get('age', -1)
    gross = request.json.get('gross', 0)

    graph.add_vertex('Actor', name, age, gross)

    return jsonify({'result': 'Created Actor'}), 201


@app.route('/api/a/movies/', methods=['POST'])
def create_movie():
    """
    Create a movie object with given attributes, if valid
    :return:
    """
    if not request.json or 'name' not in request.json:
        abort(400)

    name = request.json['name']
    year = request.json.get('year', -1)
    gross = request.json.get('gross', 0)

    graph.add_vertex('Movie', name, year, gross)

    return jsonify({'result': 'Created Movie'}), 201


""" DELETE METHODS """


@app.route('/api/a/actors/<string:actor_name>', methods=['DELETE'])
def delete_actor(actor_name):
    """
    Delete an actor object, if it exists
    :param actor_name: The name of the actor whose meta-info will be deleted
    :return:
    """
    if actor_name not in graph.get_vertices():
        abort(400)

    actor_meta = graph.get_vertex(actor_name)

    for movies in actor_meta.get_neighbors():
        actors = graph.get_vertex(movies).get_neighbors()
        del actors[actor_name]

    graph.delete_vertex(actor_name)

    return jsonify({'result': f'Deleted {actor_name}'})


@app.route('/api/a/movies/<string:movie_name>', methods=['DELETE'])
def delete_movie(movie_name):
    """
    Delete a movie object, if it exists
    :param movie_name: The name of the movie whose meta-info will be deleted
    :return:
    """
    if movie_name not in graph.get_vertices():
        abort(400)

    movie_meta = graph.get_vertex(movie_name)

    for actors in movie_meta.get_neighbors():
        movies = graph.get_vertex(actors).get_neighbors()
        del movies[movie_name]

    graph.delete_vertex(movie_name)

    return jsonify({'result': f'Deleted {movie_name}'})


""" ERROR HANDLERS """


@app.errorhandler(404)
def not_found(error):
    """
    Handle not found errors
    :param error: NOT FOUND error
    :return:
    """
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    """
    Handle bad request errors
    :param error: BAD REQUEST error
    :return:
    """
    return make_response(jsonify({'error': 'Bad Request'}), 400)
