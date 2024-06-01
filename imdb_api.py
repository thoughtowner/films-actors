from os import getenv

import requests
from dotenv import load_dotenv

import config

load_dotenv()


# {"error":{"code":110,"message":"Not found"},"about":{"version":"2.51.1","serverTime":"2024/06/01 13:10:10"}}

class ForeignApiError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f'External API request error, error code: {status_code}')


def get_data(options: dict) -> dict:
    entities = {
        'film': 'idIMDB',
        'actor': 'idName'
    }
    default_options = {'token': getenv('MYAPIFILMS_KEY'), 'format': 'json', 'language': 'en-us'}
    entity = list(options.keys())[0]
    options[entities[entity]] = options.pop(entity)
    options.update(default_options)
    response = requests.get(config.MYAPIFILMS_URL, params=options, timeout=10)
    if response.status_code != config.OK:
        raise ForeignApiError(response.status_code)
    return response.json()


def get_film_data(imbd_id: str):
    all_film_data = get_data({'film': imbd_id})['data']['movies'][0]
    film_data = {}
    film_data['title'] = all_film_data['title']
    film_data['imdb_rating'] = all_film_data['rating']
    film_data['year'] = all_film_data['year']
    film_data['country'] = all_film_data['countries'][0]
    film_data['poster'] = all_film_data['urlPoster']
    return film_data


def get_actor_data(imbd_id: str):
    all_actor_data = get_data({'actor': imbd_id, 'bornDied': 1})['data']['names'][0]
    actor_data = {}
    actor_data['full_name'] = all_actor_data['name']
    actor_data['height'] = all_actor_data['height']
    actor_data['birth_date'] = all_actor_data['bornDeath']['birthdate']
    actor_data['place_of_birth'] = all_actor_data['bornDeath']['placeOfBirth']
    actor_data['photo'] = all_actor_data['urlPhoto']
    return actor_data

# print(get_film_data('tt0111161'))
# print(get_actor_data('nm0578853'))

# def get_film_actors(imbd_id: str):
#     actors = get_data({'film': imbd_id, 'actors': 1})['data']['movies'][0]['actors']