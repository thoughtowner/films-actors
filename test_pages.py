import json

import pytest
import requests

import config

film_data = {
    'imbd_id': 'tt0069281'
}

actor_data = {
    'imdb_id': 'nm0000059'
}

CREATE = 'create'
UPDATE = 'update'
DELETE = 'delete'
HEADERS = {'Content-Type': 'application/json'}
URL = 'http://127.0.0.1:5000/'
PATHS = ('', 'add_film', 'actors', 'films')
LINKS = [f'{URL}{path}' for path in PATHS]
POST_DATA = (
    ('film', film_data),
    ('actor', actor_data),
)


@pytest.mark.parametrize('link', LINKS)
def test_get(link: str) -> None:
    response = requests.get(link, timeout=10)
    assert response.status_code == config.OK


@pytest.mark.parametrize('model, model_data', POST_DATA)
def test_post_delete(model: str, model_data: dict) -> None:
    if model == 'actor':
        film_id = requests.post(
            f'{URL}film/{CREATE}',
            headers=HEADERS,
            data=json.dumps(film_data),
            timeout=10,
        )
        model_data['film_id'] = film_id.content.decode()

    create_ok = requests.post(
        f'{URL}{model}/{CREATE}',
        headers=HEADERS,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert create_ok.status_code == config.CREATED

    create_bad_req = requests.post(
        f'{URL}{model}/{CREATE}',
        headers=HEADERS,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert create_bad_req.status_code == config.BAD_REQUEST

    model_data['id'] = create_ok.content.decode()
    update_ok = requests.put(
        f'{URL}{model}/{UPDATE}',
        headers=HEADERS,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert update_ok.status_code == config.OK

    delete_no_cont = requests.delete(
        f'{URL}{model}/{DELETE}',
        headers=HEADERS,
        data=json.dumps({'id': model_data['id']}),
        timeout=10,
    )
    assert delete_no_cont.status_code == config.NO_CONTENT

    if model == 'actor':
        requests.delete(
            f'{URL}actor/{DELETE}',
            headers=HEADERS,
            data=json.dumps({'id': film_id.content.decode()}),
            timeout=10,
        )

    update_bad_req = requests.put(
        f'{URL}{model}/{UPDATE}',
        headers=HEADERS,
        data=json.dumps(model_data),
        timeout=10,
    )
    assert update_bad_req.status_code == config.BAD_REQUEST

    delete_bad_req = requests.delete(
        f'{URL}{model}/{DELETE}',
        headers=HEADERS,
        data=json.dumps({'id': model_data['id']}),
        timeout=10,
    )
    assert delete_bad_req.status_code == config.BAD_REQUEST
