import os
from typing import Callable
from uuid import UUID

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.exc import DataError, IntegrityError, ProgrammingError
from sqlalchemy.orm import Session, exc

from imdb_api import get_film_data, get_actor_data
from models import Film, Actor


def get_db_url() -> str:
    load_dotenv()
    pg_vars = 'PG_USER', 'PG_PASSWORD', 'PG_HOST', 'PG_PORT', 'PG_DBNAME'
    credentials = [os.environ.get(pg_var) for pg_var in pg_vars]
    return 'postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(*credentials)


engine = create_engine(get_db_url(), echo=False)


def add_film_api(imbd_id: str, session: Session) -> Film | None:
    film = session.scalar(select(Film).where(Film.imbd_id == imbd_id))
    if film:
        return film
    film_data = get_film_data(imbd_id)
    if film_data:
        film = Film(imbd_id, title=film_data[0], imdb_rating=film_data[1], year=film_data[2], country=film_data[3], poster=film_data[4])
        session.add(film)
        session.commit()
        return film
    return None


def add_actor_api(imbd_id: str, session: Session) -> Actor | None:
    actor = session.scalar(select(Actor).where(Actor.imbd_id == imbd_id))
    if actor:
        return actor
    actor_data = get_actor_data(imbd_id)
    if actor_data:
        actor = Actor(imbd_id, full_name=actor_data[0], height=actor_data[1], birth_date=actor_data[2], place_of_birth=actor_data[3], photo=actor_data[4])
        session.add(actor)
        session.commit()
        return actor
    return None