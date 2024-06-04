"""Flask module with methods for managing films and actors."""


from os import environ
from uuid import UUID

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

import config
import db

load_dotenv()


app = Flask(__name__)
app.json.ensure_ascii = False
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
engine = db.engine


class AddFilmForm(FlaskForm):
    """Form for adding a new film."""

    imdb_id = StringField('Enter the film imdb_id: ')
    submit = SubmitField('Submit')


db_session = db.Session(engine)


@app.route('/')
def homepage():
    """
    Homepage route that displays all films.

    Returns:
        A rendered template of index.html with all films data.
    """
    with db_session as session:
        films = {'films': db.get_all_films(session)}
    return render_template('index.html', **films), config.OK


@app.route('/film/<film_id>')
def film(film_id: UUID):
    """
    Route to display details about a specific film.

    Args:
        film_id (UUID): The unique identifier for the film.

    Returns:
        A rendered template of film.html with the film's data and its actors.
    """
    with db_session as session:
        film_data = db.get_film(film_id, session)
        actors = db.get_film_actors(film_data['id'], session)
    film_actors = {
        'actors': actors,
    }
    return render_template('film.html', **film_actors), config.OK


@app.route('/actor/<actor_id>')
def actor(actor_id: UUID):
    """
    Render a page displaying detailed information about a specific actor.

    Args:
        actor_id (UUID): The unique identifier of the actor to display.

    Returns:
        tuple: A tuple containing the rendered HTML template \
            and an HTTP status code indicating success. \
                The template displays detailed information about the specified actor.
    """
    with db_session as session:
        actor_info = db.get_actor(actor_id, session)
    actor_data = {
        'actor': actor_info,
    }
    return render_template('actor.html', **actor_data), config.OK


@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    """
    Route for adding a new film through a form submission.

    Returns:
        Redirects to the newly added film's page on success, \
            otherwise renders add_film.html with a message.
    """
    form = AddFilmForm()
    msg = ''
    flag = False
    film_id = None
    if form.validate_on_submit():
        with db_session as session:
            film_id = db.add_film_api(form.imdb_id.data, session)
        flag = True
    if film_id:
        return redirect(f'/film/{film_id}')
    if flag:
        msg = 'The film was not found, check the correctness of the entered imdb_id'
    message = {'msg': msg}
    return render_template('add_film.html', **message, form=form), config.OK


@app.post('/<model>/create')
def create_model(model: str):
    """
    Create a new record based on the provided model.

    Args:
        model (str): The type of record to create ('film' or 'actor').

    Returns:
        The ID of the created record on success, otherwise an error status code.
    """
    body = request.json
    functions = {
        'film': db.add_film,
        'actor': db.add_actor,
        'film_to_actor': db.add_film_to_actor,
    }
    if model in functions.keys():
        with db_session as session:
            res = functions[model](body, session)
    else:
        return '', config.NOT_FOUND
    if res:
        return str(res), config.CREATED
    return '', config.BAD_REQUEST


@app.put('/<model>/update')
def update_model(model: str):
    """
    Update an existing record based on the provided model.

    Args:
        model (str): The type of record to update ('film' or 'actor').

    Returns:
        The updated record's ID on success, otherwise an error status code.
    """
    body = request.json
    functions = {
        'film': db.update_film,
        'actor': db.update_actor,
        'film_to_actor': db.update_film_to_actor,
    }
    if model in functions.keys():
        with db_session as session:
            res = functions[model](body, session)
    else:
        return '', config.NOT_FOUND
    if res:
        return str(res), config.OK
    return '', config.BAD_REQUEST


@app.delete('/<model>/delete')
def delete_model(model: str):
    """
    Delete an existing record based on the provided model.

    Args:
        model (str): The type of record to delete ('film' or 'actor').

    Returns:
        No content on successful deletion, otherwise an error status code.
    """
    body = request.json
    functions = {
        'film': db.delete_film,
        'actor': db.delete_actor,
        'film_to_actor': db.delete_film_to_actor,
    }
    if model in functions.keys():
        with db_session as session:
            res = functions[model](body['id'], session)
    else:
        return '', config.NOT_FOUND
    if res:
        return '', config.NO_CONTENT
    return '', config.BAD_REQUEST


@app.get('/<model>')
def get_model_all(model: str):
    """
    Retrieve all records of a specified model.

    Args:
        model (str): The type of records to retrieve ('films' or 'actors').

    Returns:
        A JSON response containing all records of the specified model, \
            otherwise an error status code.
    """
    functions = {
        'films': db.get_all_films,
        'actors': db.get_all_actors,
    }
    if model in functions.keys():
        with db_session as session:
            res = {f'{model}': functions[model](session)}
    else:
        return '', config.NOT_FOUND
    if res:
        return jsonify(res), config.OK
    return '', config.BAD_REQUEST


if __name__ == '__main__':
    app.run(debug=False)
