from datetime import datetime

from os import getenv

import requests
from dotenv import load_dotenv

import config

load_dotenv()


# {"error":{"code":110,"message":"Not found"},"about":{"version":"2.51.1","serverTime":"2024/06/01 13:10:10"}}

class ForeignApiError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f'External API request error, error code: {status_code}')


# def get_data(options: dict) -> dict:
#     entities = {
#         'film': 'idIMDB',
#         'actor': 'idName'
#     }
#     default_options = {'token': getenv('MYAPIFILMS_KEY'), 'format': 'json', 'language': 'en-us'}
#     entity = list(options.keys())[0]
#     options[entities[entity]] = options.pop(entity)
#     options.update(default_options)
#     response = requests.get(config.MYAPIFILMS_URL, params=options, timeout=10)
#     if response.status_code != config.OK:
#         raise ForeignApiError(response.status_code)
#     return response.json()


# def get_film_data(imbd_id: str):
#     all_film_data = get_data({'film': imbd_id})['data']['movies'][0]
#     film_data = {}
#     film_data['title'] = all_film_data['title']
#     film_data['imdb_rating'] = all_film_data['rating']
#     film_data['year'] = all_film_data['year']
#     film_data['country'] = all_film_data['countries'][0]
#     film_data['poster'] = all_film_data['urlPoster']
#     return film_data


# def get_actor_data(imbd_id: str):
#     all_actor_data = get_data({'actor': imbd_id, 'bornDied': 1})['data']['names'][0]
#     actor_data = {}
#     actor_data['full_name'] = all_actor_data['name']
#     actor_data['height'] = all_actor_data['height']
#     actor_data['birth_date'] = all_actor_data['bornDeath']['birthdate']
#     actor_data['place_of_birth'] = all_actor_data['bornDeath']['placeOfBirth']
#     actor_data['photo'] = all_actor_data['urlPhoto']
#     return actor_data

# print(get_film_data('tt0111161'))
# print(get_actor_data('nm0578853'))



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


def get_film_data(imbd_id: str):
    data = get_data({'film': imbd_id})
    if data['error']:
        return None
    all_film_data = data['data']['movies'][0]
    non_sequence_fields = {'title': 'title', 'imdb_rating': 'rating', 'year': 'year', 'poster': 'urlPoster'}
    country = {'country': 'countries'}
    country_key = list(country.keys())[0]

    film_data = {'imbd_id': imbd_id}
    for model_field, api_field in non_sequence_fields.items():
        film_data[model_field] = all_film_data.get(api_field, None)
    country_api_value = all_film_data.get(country[country_key], None)
    film_data[country_key] = country_api_value[0] if country_api_value else None
    return film_data


def get_actor_data(imbd_id: str):
    data = get_data({'actor': imbd_id, 'bornDied': 1})
    all_actor_data = data['data']['names'][0]
    non_sequence_fields = {'full_name': 'name', 'height': 'height', 'photo': 'urlPhoto'}
    born_death = 'bornDeath'
    born_death_fields = {'birth_date': 'birthdate', 'place_of_birth': 'placeOfBirth'}

    actor_data = {'imbd_id': imbd_id}
    for model_field, api_field in non_sequence_fields.items():
        actor_data[model_field] = all_actor_data.get(api_field, None)
    if all_actor_data[born_death]:
        for model_field, api_field in born_death_fields.items():
            born_death_api_value = all_actor_data[born_death].get(api_field, None)
            if model_field == 'birth_date':
                if born_death_api_value:
                    born_death_api_value = datetime.strptime(born_death_api_value, '%Y%m%d').date()
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

# print(get_film_data('tt0069281'))
# print(get_film_actors_data('tt0069281'))