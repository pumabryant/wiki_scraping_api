from flask import Flask, jsonify, request, make_response, abort
import parse_data
app = Flask(__name__)

graph = parse_data.parse('data.json')


""" GET METHODS """


@app.route('/')
def index():
    return "Actor and Movie API"


@app.route('/actors', methods=['GET'])
def get_filtered_actors():
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
    :param name:
    :param value_1:
    :param value_2:
    :param filter_names:
    :param filter_value1:
    :param filter_value2:
    :return:
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

    actor_meta = {}
    for vertex in graph:
        if vertex.get_group() == 'Actor' and vertex.get_key() == actor_name:
            actor = dict()
            actor['name'] = vertex.get_key()
            actor['age'] = vertex.get_value1()
            actor['gross'] = vertex.get_value2()
            actor_meta[actor_name] = actor

    return jsonify(actor_meta)


@app.route('/actors/<movie_title>', methods=['GET'])
def get_movie(movie_title):

    movie_meta = {}
    for vertex in graph:
        if vertex.get_group() == 'Movie' and vertex.get_key() == movie_meta:
            movie = dict()
            movie['title'] = vertex.get_key()
            movie['year'] = vertex.get_value1()
            movie['gross'] = vertex.get_value2()
            movie_meta[movie_title] = movie

    return jsonify(movie_meta)


""" PUT METHODS """


@app.route('/api/a/actors/<string:actor_name>', methods=['PUT'])
def update_actor(actor_name):
    if actor_name is None or actor_name not in graph.get_vertices():
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
    if movie_name is None or movie_name not in graph.get_vertices():
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
    if not request.json or 'name' not in request.json:
        abort(400)

    name = request.json['name']
    age = request.json.get('age', -1)
    gross = request.json.get('gross', 0)
    actor = {
        'name': name,
        'age': age,
        'gross': gross
    }

    return jsonify({name: actor}), 201


@app.route('/api/a/movies/', methods=['POST'])
def create_movie():
    if not request.json or 'name' not in request.json:
        abort(400)

    name = request.json['name']
    year = request.json.get('year', -1)
    gross = request.json.get('gross', 0)
    movie = {
        'name': name,
        'year': year,
        'gross': gross
    }

    return jsonify({name: movie}), 201


""" DELETE METHODS """


@app.route('/api/a/actors/<string:actor_name>', methods=['DELETE'])
def delete_actor(actor_name):
    return


@app.route('/api/a/actors/<string:movie_name>', methods=['DELETE'])
def delete_movie(movie_name):
    return


""" ERROR HANDLERS """


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)

