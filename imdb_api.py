from datetime import datetime
from os import getenv

import requests
from dotenv import load_dotenv

import config

load_dotenv()


class ForeignApiError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f'External API request error, error code: {status_code}')


def get_data(options: dict) -> dict:
    entities = {
        'film': 'idIMDB',
        'actor': 'idName'
    }
    default_options = {'token': getenv('MYAPIFILMS_KEY'), 'format': 'json', 'language': 'en-us'}

    entities_keys = list(entities.keys())
    for option_key in list(options.keys()):
        if option_key in entities_keys:
            entity = option_key

    options[entities[entity]] = options.pop(entity)
    options.update(default_options)
    response = requests.get(config.MYAPIFILMS_URL, params=options, timeout=10)
    if response.status_code != config.OK:
        raise ForeignApiError(response.status_code)
    return response.json()


def add_non_sequence_fields(non_sequence_fields: dict, model_data: dict, all_model_data: dict):
    for model_field, api_field in non_sequence_fields.items():
        model_data[model_field] = all_model_data.get(api_field, None)
    return model_data


def get_film_data(imbd_id: str):
    data = get_data({'film': imbd_id})
    if data['error']:
        return None
    all_film_data = data['data']['movies'][0]
    non_sequence_fields = {
        'title': 'title',
        'imdb_rating': 'rating',
        'year': 'year',
        'poster': 'urlPoster'}
    country = {'country': 'countries'}
    country_key = list(country.keys())[0]

    film_data = {'imbd_id': imbd_id}
    film_data = add_non_sequence_fields(non_sequence_fields, film_data, all_film_data)
    country_api_value = all_film_data.get(country[country_key], None)
    film_data[country_key] = country_api_value[0] if country_api_value else None
    return film_data


def get_actor_data(imbd_id: str):
    data = get_data({'actor': imbd_id, 'bornDied': 1})
    all_actor_data = data['data']['names'][0]
    non_sequence_fields = {
        'full_name': 'name',
        'height': 'height',
        'photo': 'urlPhoto'
    }
    born_death = 'bornDeath'
    born_death_fields = {
        'birth_date': 'birthdate',
        'place_of_birth': 'placeOfBirth'
    }

    actor_data = {'imbd_id': imbd_id}
    actor_data = add_non_sequence_fields(non_sequence_fields, actor_data, all_actor_data)
    if all_actor_data[born_death]:
        for model_field, api_field in born_death_fields.items():
            born_death_api_value = all_actor_data[born_death].get(api_field, None)
            if model_field == 'birth_date':
                if born_death_api_value:
                    born_death_api_value = datetime.strptime(
                        born_death_api_value, '%Y%m%d'
                    ).date()
            elif model_field == 'place_of_birth':
                if born_death_api_value == '':
                    born_death_api_value = None
            actor_data[model_field] = born_death_api_value
    else:
        for model_field in born_death_fields.keys():
            actor_data[model_field] = None
    return actor_data


def get_film_actors_data(imbd_id: str):
    data = get_data({'film': imbd_id, 'actors': 1})
    if data['error']:
        return None
    film_actors = data['data']['movies'][0]['actors']
    actors_data_list = []
    for actor in film_actors:
        actor_imbd_id = actor['idIMDB']
        actor_data = get_actor_data(actor_imbd_id)
        actors_data_list.append(actor_data)
    return actors_data_list
