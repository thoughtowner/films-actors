"""A module for working with an external imdb api (MYAPIFILMS)."""


# from datetime import datetime
import datetime
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
    response = requests.get(config.MYAPIFILMS_URL, params=options, timeout=30)
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


def get_film_data(imdb_id: str):
    """
    Retrieve detailed film data from an external API.

    Args:
        imdb_id (str): The IMDb ID of the film to fetch data for.

    Returns:
        dict: A dictionary containing formatted film data.
    """
    all_data = get_data({'film': imdb_id})
    if 'error' in all_data:
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

    film_data = {'imdb_id': imdb_id}
    film_data = add_non_sequence_fields(non_sequence_fields, film_data, all_film_data)
    country_api_value = all_film_data.get(country[country_key], None)
    film_data[country_key] = country_api_value[0]
    return film_data


def get_actor_data(imdb_id: str):
    """
    Retrieve detailed actor data from an external API.

    Args:
        imdb_id (str): The IMDb ID of the actor to fetch data for.

    Returns:
        dict: A dictionary containing formatted actor data.
    """
    all_data = get_data({'actor': imdb_id, 'bornDied': 1})
    non_sequence_fields = {
        'full_name': 'name',
        'height': 'height',
        'photo': 'urlPhoto',
    }
    born_death_fields = {
        'birth_date': 'birthdate',
        'place_of_birth': 'placeOfBirth',
    }

    actor_data = {'imdb_id': imdb_id}
    actor_data = add_non_sequence_fields(
        non_sequence_fields, actor_data, all_data['data']['names'][0],
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


def get_film_actors_data(imdb_id: str):
    """
    Retrieve a list of actors associated with a film from an external API.

    Args:
        imdb_id (str): The IMDb ID of the film whose actors' data is to be fetched.

    Returns:
        list: A list of dictionaries, \
            each containing formatted data for an actor associated with the film.
    """
    all_data = get_data({'film': imdb_id, 'actors': 1})
    if 'error' in all_data:
        return None
    film_actors = all_data['data']['movies'][0]['actors']
    film_actors = film_actors if len(film_actors) <= 5 else film_actors[:5]
    actors_data_list = []
    for actor in film_actors:
        actor_imdb_id = actor['idIMDB']
        actor_data = get_actor_data(actor_imdb_id)
        actors_data_list.append(actor_data)
    return actors_data_list






def get_film_data_from_tg(imdb_id: str):
    all_films = [
        {'imdb_id': 'tt0137523', 'title': 'Fight Club', 'imdb_rating': 8.8, 'year': 1999, 'poster': 'https://m.media-amazon.com/images/M/MV5BMmEzNTkxYjQtZTc0MC00YTVjLTg5ZTEtZWMwOWVlYzY0NWIwXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_FMjpg_UX1000_.jpg', 'country': 'Germany'},
        {'imdb_id': 'tt0068646', 'title': 'The Godfather', 'imdb_rating': 9.2, 'year': 1972, 'poster': 'https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_FMjpg_UX1000_.jpg', 'country': 'United States'},
        {'imdb_id': 'tt6966692', 'title': 'Green Book', 'imdb_rating': 8.2, 'year': 2018, 'poster': 'https://m.media-amazon.com/images/M/MV5BYzIzYmJlYTYtNGNiYy00N2EwLTk4ZjItMGYyZTJiOTVkM2RlXkEyXkFqcGdeQXVyODY1NDk1NjE@._V1_FMjpg_UX1000_.jpg', 'country': 'United States'},
        {'imdb_id': 'tt0109830', 'title': 'Forrest Gump', 'imdb_rating': 8.8, 'year': 1994, 'poster': 'https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_FMjpg_UX1000_.jpg', 'country': 'United States'},
        {'imdb_id': 'tt1853728', 'title': 'Django Unchained', 'imdb_rating': 8.5, 'year': 2012, 'poster': 'https://m.media-amazon.com/images/M/MV5BMjIyNTQ5NjQ1OV5BMl5BanBnXkFtZTcwODg1MDU4OA@@._V1_FMjpg_UX1000_.jpg', 'country': 'United States'}
    ]
    if imdb_id == 'tt0137523':
        return all_films[0]
    if imdb_id == 'tt0068646':
        return all_films[1]
    if imdb_id == 'tt6966692':
        return all_films[2]
    if imdb_id == 'tt0109830':
        return all_films[3]
    if imdb_id == 'tt1853728':
        return all_films[4]
    

def get_film_actors_data_from_tg(imdb_id: str):
    all_film_actors = [
        [{'imdb_id': 'nm0000093', 'full_name': 'Brad Pitt', 'height': "5' 11″ (1.80 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMjA1MjE2MTQ2MV5BMl5BanBnXkFtZTcwMjE5MDY0Nw@@._V1_QL75_UX90_CR0,1,90,133_.jpg', 'birth_date': datetime.date(1963, 12, 18), 'place_of_birth': 'Shawnee, Oklahoma, USA'}, {'imdb_id': 'nm0001570', 'full_name': 'Edward Norton', 'height': "6' (1.83 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTYwNjQ5MTI1NF5BMl5BanBnXkFtZTcwMzU5MTI2Mw@@._V1_QL75_UY133_CR7,0,90,133_.jpg', 'birth_date': datetime.date(1969, 8, 18), 'place_of_birth': 'Boston, Massachusetts, USA'}, {'imdb_id': 'nm0001533', 'full_name': 'Meat Loaf', 'height': "6' (1.83 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTIzNTQ4MjYyOV5BMl5BanBnXkFtZTcwNzgwNTEzMg@@._V1_QL75_UY133_CR3,0,90,133_.jpg', 'birth_date': datetime.date(1947, 9, 27), 'place_of_birth': 'Dallas, Texas, USA'}, {'imdb_id': 'nm0340260', 'full_name': 'Zach Grenier', 'height': "5' 9″ (1.75 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BNjg3MzQxMDAxN15BMl5BanBnXkFtZTgwODMwNTk5ODE@._V1_QL75_UY133_CR12,0,90,133_.jpg', 'birth_date': None, 'place_of_birth': 'Englewood, New Jersey, USA'}, {'imdb_id': 'nm0037118', 'full_name': 'Richmond Arquette', 'height': "5' 10″ (1.78 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMjM1NDgxOTQwM15BMl5BanBnXkFtZTgwNzEyNjg4MDE@._V1_QL75_UY133_CR74,0,90,133_.jpg', 'birth_date': datetime.date(1963, 8, 21), 'place_of_birth': 'New York City, New York, USA'}],
        [{'imdb_id': 'nm0000008', 'full_name': 'Marlon Brando', 'height': "5' 8¾″ (1.75 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTg3MDYyMDE5OF5BMl5BanBnXkFtZTcwNjgyNTEzNA@@._V1_QL75_UY133_CR41,0,90,133_.jpg', 'birth_date': datetime.date(1924, 4, 3), 'place_of_birth': 'Omaha, Nebraska, USA'}, {'imdb_id': 'nm0000199', 'full_name': 'Al Pacino', 'height': "5' 6″ (1.68 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTQzMzg1ODAyNl5BMl5BanBnXkFtZTYwMjAxODQ1._V1_QL75_UX90_CR0,1,90,133_.jpg', 'birth_date': datetime.date(1940, 4, 25), 'place_of_birth': 'Manhattan, New York City, New York, USA'}, {'imdb_id': 'nm0001001', 'full_name': 'James Caan', 'height': "5' 9¼″ (1.76 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTI5NjkyNDQ3NV5BMl5BanBnXkFtZTcwNjY5NTQ0Mw@@._V1_QL75_UX90_CR0,1,90,133_.jpg', 'birth_date': datetime.date(1940, 3, 26), 'place_of_birth': 'The Bronx, New York, USA'}, {'imdb_id': 'nm0000473', 'full_name': 'Diane Keaton', 'height': "5' 6½″ (1.69 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTY5NDI5OTEyOF5BMl5BanBnXkFtZTgwMzU4NDI1NzM@._V1_QL75_UY133_CR2,0,90,133_.jpg', 'birth_date': datetime.date(1946, 1, 5), 'place_of_birth': 'Los Angeles, California, USA'}, {'imdb_id': 'nm0144710', 'full_name': 'Richard S. Castellano', 'height': "5' 9″ (1.75 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMjI2MzA3MjQ5N15BMl5BanBnXkFtZTcwMzY5NDYwOA@@._V1_QL75_UY133_CR1,0,90,133_.jpg', 'birth_date': datetime.date(1933, 9, 4), 'place_of_birth': 'The Bronx, New York City, New York, USA'}],
        [{'imdb_id': 'nm0001557', 'full_name': 'Viggo Mortensen', 'height': "5' 11″ (1.80 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BNDQzOTg4NzA2Nl5BMl5BanBnXkFtZTcwMzkwNjkxMg@@._V1_QL75_UX90_CR0,0,90,133_.jpg', 'birth_date': datetime.date(1958, 10, 20), 'place_of_birth': 'Manhattan, New York City, New York, USA'}, {'imdb_id': 'nm0991810', 'full_name': 'Mahershala Ali', 'height': "6' 2″ (1.88 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BZThiZjJjNWYtNGRlYS00NDdkLTk0MTMtYjEwYzM1MDExNTYwXkEyXkFqcGdeQXVyNjY1MTg4Mzc@._V1_QL75_UY133_CR16,0,90,133_.jpg', 'birth_date': datetime.date(1974, 2, 16), 'place_of_birth': 'Oakland, California, USA'}, {'imdb_id': 'nm0004802', 'full_name': 'Linda Cardellini', 'height': "5' 3″ (1.60 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTQ2MDM4MTM2NF5BMl5BanBnXkFtZTgwMTM4MjYyMDE@._V1_QL75_UY133_CR3,0,90,133_.jpg', 'birth_date': datetime.date(1975, 6, 25), 'place_of_birth': 'Redwood City, California, USA'}, {'imdb_id': 'nm1724319', 'full_name': 'Sebastian Maniscalco', 'height': "5' 9″ (1.75 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BOTA0OWM4NWUtMTRiOC00MzM3LTk3NzktMjQyNjIyOGI4ZjUyXkEyXkFqcGdeQXVyMTI5OTE4MzM@._V1_QL75_UX90_CR0,1,90,133_.jpg', 'birth_date': datetime.date(1973, 7, 8), 'place_of_birth': 'Chicago, Illinois, USA'}, {'imdb_id': 'nm1221253', 'full_name': 'Dimiter D. Marinov', 'height': "5' 8″ (1.73 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BYzMwMjZiZmItMGE4MC00MGMyLTliYzctZWY0MWUyZThiNmZmXkEyXkFqcGdeQXVyMjE4ODQyODU@._V1_QL75_UY133_CR10,0,90,133_.jpg', 'birth_date': None, 'place_of_birth': None}],
        [{'imdb_id': 'nm0000158', 'full_name': 'Tom Hanks', 'height': "6' (1.83 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTQ2MjMwNDA3Nl5BMl5BanBnXkFtZTcwMTA2NDY3NQ@@._V1_QL75_UY133_CR1,0,90,133_.jpg', 'birth_date': datetime.date(1956, 7, 9), 'place_of_birth': 'Concord, California, USA'}, {'imdb_id': 'nm0000705', 'full_name': 'Robin Wright', 'height': "5' 5″ (1.65 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTU0NTc4MzEyOV5BMl5BanBnXkFtZTcwODY0ODkzMQ@@._V1_QL75_UY133_CR2,0,90,133_.jpg', 'birth_date': datetime.date(1966, 4, 8), 'place_of_birth': 'Dallas, Texas, USA'}, {'imdb_id': 'nm0000641', 'full_name': 'Gary Sinise', 'height': "5' 8″ (1.73 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMzE4NzcyMzU3OV5BMl5BanBnXkFtZTYwOTM2NDE2._V1_QL75_UY133_CR3,0,90,133_.jpg', 'birth_date': datetime.date(1955, 3, 17), 'place_of_birth': 'Blue Island, Illinois, USA'}, {'imdb_id': 'nm0000398', 'full_name': 'Sally Field', 'height': "5' 2″ (1.57 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTQwOTMyMDI4MV5BMl5BanBnXkFtZTcwMDYzMTM5OA@@._V1_QL75_UY133_CR4,0,90,133_.jpg', 'birth_date': datetime.date(1946, 11, 6), 'place_of_birth': 'Pasadena, California, USA'}, {'imdb_id': 'nm0931508', 'full_name': 'Rebecca Williams', 'height': None, 'photo': 'https://m.media-amazon.com/images/M/MV5BZGVmNzAzODctNjI4MS00MzI2LThiZDItOGIyZGJlNDZmZDI5XkEyXkFqcGdeQXVyNjUxMjc1OTM@._V1_QL75_UY133_CR84,0,90,133_.jpg', 'birth_date': None, 'place_of_birth': None}],
        [{'imdb_id': 'nm0004937', 'full_name': 'Jamie Foxx', 'height': "5' 9″ (1.75 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTkyNjY1NDg3NF5BMl5BanBnXkFtZTgwNjA2MTg0MzE@._V1_QL75_UY133_CR5,0,90,133_.jpg', 'birth_date': datetime.date(1967, 12, 13), 'place_of_birth': 'Terrell, Texas, USA'}, {'imdb_id': 'nm0910607', 'full_name': 'Christoph Waltz', 'height': "5' 7″ (1.70 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTM4MDk3OTYxOF5BMl5BanBnXkFtZTcwMDk5OTUwOQ@@._V1_QL75_UY133_CR4,0,90,133_.jpg', 'birth_date': datetime.date(1956, 10, 4), 'place_of_birth': 'Vienna, Austria'}, {'imdb_id': 'nm0000138', 'full_name': 'Leonardo DiCaprio', 'height': "6' (1.83 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMjI0MTg3MzI0M15BMl5BanBnXkFtZTcwMzQyODU2Mw@@._V1_QL75_UY133_CR5,0,90,133_.jpg', 'birth_date': datetime.date(1974, 11, 11), 'place_of_birth': 'Hollywood, Los Angeles, California, USA'}, {'imdb_id': 'nm0913488', 'full_name': 'Kerry Washington', 'height': "5' 4″ (1.63 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTUxNzk2OTQzOF5BMl5BanBnXkFtZTcwMTM0NjIwNw@@._V1_QL75_UY133_CR11,0,90,133_.jpg', 'birth_date': datetime.date(1977, 1, 31), 'place_of_birth': 'The Bronx, New York City, New York, USA'}, {'imdb_id': 'nm0000168', 'full_name': 'Samuel L. Jackson', 'height': "6' 2½″ (1.89 m)", 'photo': 'https://m.media-amazon.com/images/M/MV5BMTQ1NTQwMTYxNl5BMl5BanBnXkFtZTYwMjA1MzY1._V1_QL75_UX90_CR0,1,90,133_.jpg', 'birth_date': datetime.date(1948, 12, 21), 'place_of_birth': 'Washington D.C., USA'}]
    ]
    if imdb_id == 'tt0137523':
        return all_film_actors[0]
    if imdb_id == 'tt0068646':
        return all_film_actors[1]
    if imdb_id == 'tt6966692':
        return all_film_actors[2]
    if imdb_id == 'tt0109830':
        return all_film_actors[3]
    if imdb_id == 'tt1853728':
        return all_film_actors[4]