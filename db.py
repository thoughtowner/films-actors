import os
from typing import Callable
from uuid import UUID

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.exc import DataError, IntegrityError, ProgrammingError
from sqlalchemy.orm import Session, exc

from films_api import get_film_data, get_film_actors_data
from models import Film, Actor, FilmToActor


def get_db_url() -> str:
    load_dotenv()
    PG_VARS = 'PG_HOST', 'PG_PORT', 'PG_USER', 'PG_PASSWORD', 'PG_DBNAME'
    credentials = {var: os.environ.get(var) for var in PG_VARS}
    return 'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}'.format(**credentials)


engine = create_engine(get_db_url(), echo=False)


def add_film_api(imbd_id: str, session: Session) -> Film | None:
    film = session.scalar(select(Film).where(Film.imbd_id == imbd_id))
    if film:
        return film
    film_data = get_film_data(imbd_id)
    if film_data:
        film = Film(**film_data)
        session.add(film)
        session.commit()
        return film
    return None

def add_actors_api(film_id: Film, imbd_id: str, session: Session):
    actors_data = get_film_actors_data(imbd_id)
    actors = [Actor(**actor_data) for actor_data in actors_data]
    session.add_all(actors)
    session.flush()
    film_to_actors = [FilmToActor(film_id=film_id, actor_id=actor.id) for actor in actors]
    session.add_all(film_to_actors)
    session.commit()


# def delete_empty_relations(object_id: str, object_model, session: Session):
#     if not object_id:
#         return
#     if object_model == Film:
#         actors = session.scalars(select(FilmToActor).where(FilmToActor.film_id == object_id)).all()
#     elif object_model == Actor:
#         films = session.scalars(select(FilmToActor).where(FilmToActor.actor_id == object_id)).all()
#     if not (actors or films):
#         session.delete(session.scalar(select(object_model).where(object_model.id == object_id)))
#         session.commit()

def create_delete(object_model) -> Callable:
    def delete_object(object_id: UUID, session: Session) -> int | None:
        try:
            object = session.scalar(select(object_model).where(object_model.id == object_id))
            if not object:
                return None
            session.delete(object)
            session.commit()
            # delete_empty_relations(object.id, Actor, session)
            return 1
        except DataError:
            return None
    return delete_object

delete_film = create_delete(Film)
delete_actor = create_delete(Actor)


def create_add(object_model) -> Callable:
    def create_object(object_data: dict, session: Session) -> UUID | None:
        try:
            object = object_model(**object_data)
            session.add(object)
            session.commit()
            return object.id
        except IntegrityError:
            return None
        except ProgrammingError:
            return None
        except DataError:
            return None
    return create_object

create_film = create_add(Film)
create_actor = create_add(Actor)


def create_update(object_model) -> Callable:
    def update_object(new_object_data: dict, session: Session):
        try:
            session.bulk_update_mappings(object_model, [{'id': new_object_data['id'], **new_object_data}])
            session.commit()
            return new_object_data['id']
        except DataError:
            return None
        except exc.StaleDataError:
            return None
        except IntegrityError:
            return None
    return update_object

update_film = create_update(Film)
update_actor = create_update(Actor)


def create_get(object_model) -> Callable:
    def get_object(object_id: dict, session: Session) -> dict | None:
        object_data = session.scalar(select(object_model).where(object_model.id == object_id))
        if not object_data:
            return None
        return object_data.__dict__
    return get_object

get_film = create_get(Film)
get_actor = create_get(Actor)


def create_get_all(object_model) -> Callable:
    def get_all_objects(session: Session) -> list:
        objects_data = [object_.__dict__ for object_ in session.scalars(select(object_model))]
        for object_data in objects_data:
            for field, field_value in object_data.items():
                if isinstance(field_value, UUID):
                    object_data[field] = str(field_value)
        return objects_data
    return get_all_objects

get_all_films = create_get_all(Film)
get_all_actors = create_get_all(Actor)


def get_film_actors(film_id, session: Session) -> list[dict]:
    try:
        query = select(Actor).select_from(FilmToActor.__table__.join(Actor, FilmToActor.actor_id == Actor.id)).where(FilmToActor.film_id == film_id)
        actors = session.scalars(query).all()
    except DataError:
        return None
    if actors:
        return [actor.__dict__ for actor in actors]
    return None
