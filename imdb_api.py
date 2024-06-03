"""A module for working with an external imdb api (MYAPIFILMS)."""


from datetime import datetime
from os import getenv

import requests
from dotenv import load_dotenv

import config

load_dotenv()


class ForeignApiError(Exception):
    """
    Exception raise when there is an error with an external API request.

    Attributes:
        status_code (int): The HTTP status code returned by the external API.
    """

    def __init__(self, status_code: int) -> None:
        """
        Initialize the ForeignApiError exception with a custom error message.

        Args:
            status_code (int): The HTTP status code indicating the nature \
                of the error encountered during the API request.
        """
        super().__init__(f'External API request error, error code: {status_code}')


def get_data(options: dict) -> dict:
    """
    Fetch data from an external API based on provided options.

    Args:
        options (dict): Additional options to include in the API request.

    Returns:
        dict: The parsed JSON response from the API.

    Raises:
        ForeignApiError: If response status code not equal OK.
    """
    entities = {
        'film': 'idIMDB',
        'actor': 'idName',
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
    """
    Add non-sequence fields to a model data dictionary.

    Args:
        non_sequence_fields (dict): Mapping of API field names to model field names.
        model_data (dict): The model data dictionary to which fields will be added.
        all_model_data (dict): The complete data retrieved from the external API.

    Returns:
        dict: The updated model data dictionary with additional non-sequence fields.
    """
    for model_field, api_field in non_sequence_fields.items():
        model_data[model_field] = all_model_data.get(api_field, None)
    return model_data


def get_film_data(imbd_id: str):
    """
    Retrieve detailed film data from an external API.

    Args:
        imbd_id (str): The IMDb ID of the film to fetch data for.

    Returns:
        dict: A dictionary containing formatted film data.
    """
    all_data = get_data({'film': imbd_id})
    if all_data['error']:
        return None
    all_film_data = all_data['data']['movies'][0]
    non_sequence_fields = {
        'title': 'title',
        'imdb_rating': 'rating',
        'year': 'year',
        'poster': 'urlPoster',
    }
    country = {'country': 'countries'}
    country_key = list(country.keys())[0]

    film_data = {'imbd_id': imbd_id}
    film_data = add_non_sequence_fields(non_sequence_fields, film_data, all_film_data)
    country_api_value = all_film_data.get(country[country_key], None)
    film_data[country_key] = country_api_value[0] if country_api_value else None
    return film_data


def get_actor_data(imbd_id: str):
    """
    Retrieve detailed actor data from an external API.

    Args:
        imbd_id (str): The IMDb ID of the actor to fetch data for.

    Returns:
        dict: A dictionary containing formatted actor data.
    """
    all_data = get_data({'actor': imbd_id, 'bornDied': 1})
    non_sequence_fields = {
        'full_name': 'name',
        'height': 'height',
        'photo': 'urlPhoto',
    }
    born_death_fields = {
        'birth_date': 'birthdate',
        'place_of_birth': 'placeOfBirth',
    }

    actor_data = add_non_sequence_fields(
        non_sequence_fields, {'imbd_id': imbd_id}, all_data['data']['names'][0],
    )
    born_death_actor_data = all_data['data']['names'][0]['bornDeath']
    if born_death_actor_data:
        for model_field, api_field in born_death_fields.items():
            born_death_api_value = born_death_actor_data.get(api_field, None)
            if model_field == 'birth_date':
                if born_death_api_value:
                    born_death_api_value = datetime.strptime(
                        born_death_api_value, '%Y%m%d',
                    ).date()
            elif model_field == 'place_of_birth':
                if born_death_api_value == '':
                    born_death_api_value = None
            actor_data[model_field] = born_death_api_value
    else:
        for model_field_key in born_death_fields.keys():
            actor_data[model_field_key] = None
    return actor_data


def get_film_actors_data(imbd_id: str):
    """
    Retrieve a list of actors associated with a film from an external API.

    Args:
        imbd_id (str): The IMDb ID of the film whose actors' data is to be fetched.

    Returns:
        list: A list of dictionaries, \
            each containing formatted data for an actor associated with the film.
    """
    all_data = get_data({'film': imbd_id, 'actors': 1})
    if all_data['error']:
        return None
    film_actors = all_data['data']['movies'][0]['actors']
    actors_data_list = []
    for actor in film_actors:
        actor_imbd_id = actor['idIMDB']
        actor_data = get_actor_data(actor_imbd_id)
        actors_data_list.append(actor_data)
    return actors_data_list
