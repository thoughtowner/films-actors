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
    imbd_id = StringField('Enter the film imbd_id: ')
    submit = SubmitField('Submit')


@app.route('/')
def homepage():
    with db.Session(engine) as session:
        content = {'content': db.get_all_films(session)}
    return render_template('index.html', **content), config.OK


@app.route('/film/<film_id>')
def film(film_id: UUID):
    with db.Session(engine) as session:
        film_data = db.get_film(film_id, session)
        actors = db.get_film_actors(film_data['id'], session)
    content = {
        'film': film_data,
        'actors': actors,
    }
    return render_template('film.html', **content), config.OK


@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    form = AddFilmForm()
    msg = ''
    flag = False
    film_id = None
    if form.validate_on_submit():
        with db.Session(engine) as session:
            film_id = db.add_film_api(form.imbd_id.data, session)
        flag = True
    if film_id:
        return redirect(f'/film/{film_id}')
    if flag:
        msg = 'Фильм не найден, проверьте введенные данные'
    content = {'msg': msg}
    return render_template('add_film.html', **content, form=form), config.OK


@app.post('/<model>/create')
def create_model(model: str):
    body = request.json
    functions = {
        'film': db.create_film,
        'actor': db.create_actor,
    }
    if model in functions.keys():
        with db.Session(engine) as session:
            res = functions[model](body, session)
    else:
        return '', config.NOT_FOUND
    if res:
        return str(res), config.CREATED
    return '', config.BAD_REQUEST


@app.put('/<model>/update')
def update_model(model: str):
    body = request.json
    functions = {
        'film': db.update_film,
        'actor': db.update_actor,
    }
    if model in functions.keys():
        with db.Session(engine) as session:
            res = functions[model](body, session)
    else:
        return '', config.NOT_FOUND
    if res:
        return str(res), config.OK
    return '', config.BAD_REQUEST


@app.delete('/<model>/delete')
def delete_model(model: str):
    body = request.json
    functions = {
        'film': db.delete_film,
        'actor': db.delete_actor,
    }
    if model in functions.keys():
        with db.Session(engine) as session:
            res = functions[model](body['id'], session)
    else:
        return '', config.NOT_FOUND
    if res:
        return '', config.NO_CONTENT
    return '', config.BAD_REQUEST


@app.get('/<model>')
def get_model_all(model: str):
    functions = {
        'films': db.get_all_films,
        'actors': db.get_all_actors,
    }
    if model in functions.keys():
        with db.Session(engine) as session:
            res = {f'{model}': functions[model](session)}
    else:
        return '', config.NOT_FOUND
    if res:
        return jsonify(res), config.OK
    return '', config.BAD_REQUEST


if __name__ == '__main__':
    app.run(debug=False)
