"""Module for pages tests."""


import json

import pytest
import requests

import config

film_data = {'imbd_id': 'tt0069281'}
actor_data = {'imdb_id': 'nm0000059'}

CREATE = 'create'
UPDATE = 'update'
DELETE = 'delete'
URL = 'http://0.0.0.0:5000/'
PATHS = ('', 'add_film', 'actors', 'films')
POST_DATA = (
    ('film', film_data),
    ('actor', actor_data),
)

headers = {'Content-Type': 'application/json'}
links = [f'{URL}{path}' for path in PATHS]


@pytest.mark.parametrize('link', links)
def test_get(link: str) -> None:
    """
    Test HTTP GET requests to various links.

    Send a GET request to each link in the links parameter \
        and assert that the response status code is OK (200).

    Args:
        link (str): The URL to send the GET request to.
    """
    response = requests.get(link, timeout=10)
    assert response.status_code == config.OK


@pytest.mark.parametrize('model, model_data', POST_DATA)
def test_post_delete(model: str, model_data: dict) -> None:
    """
    Test creating, updating, and deleting entities via HTTP POST, PUT, and DELETE requests.

    Args:
        model (str): The name of the model to test CRUD operations on.
        model_data (dict): The data to use for creating, updating, and deleting the entity.
    """
    if model == 'actor':
        film_id = requests.post(
            f'{URL}film/{CREATE}',
            headers=headers,
            data=json.dumps(film_data),
            timeout=10,
        )
        model_data['film_id'] = film_id.content.decode()

    create_ok = requests.post(
        f'{URL}{model}/{CREATE}',
        headers=headers,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert create_ok.status_code == config.CREATED

    create_bad_req = requests.post(
        f'{URL}{model}/{CREATE}',
        headers=headers,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert create_bad_req.status_code == config.BAD_REQUEST

    model_data['id'] = create_ok.content.decode()
    update_ok = requests.put(
        f'{URL}{model}/{UPDATE}',
        headers=headers,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert update_ok.status_code == config.OK

    delete_no_cont = requests.delete(
        f'{URL}{model}/{DELETE}',
        headers=headers,
        data=json.dumps({'id': model_data['id']}),
        timeout=10,
    )
    assert delete_no_cont.status_code == config.NO_CONTENT

    if model == 'actor':
        requests.delete(
            f'{URL}actor/{DELETE}',
            headers=headers,
            data=json.dumps({'id': film_id.content.decode()}),
            timeout=10,
        )

    update_bad_req = requests.put(
        f'{URL}{model}/{UPDATE}',
        headers=headers,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert update_bad_req.status_code == config.BAD_REQUEST

    delete_bad_req = requests.delete(
        f'{URL}{model}/{DELETE}',
        headers=headers,
        data=json.dumps({'id': model_data['id']}),
        timeout=10,
    )
    assert delete_bad_req.status_code == config.BAD_REQUEST
