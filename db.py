"""A module for working with a database."""


import os
from typing import Callable
from uuid import UUID

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.exc import DataError, IntegrityError, ProgrammingError
from sqlalchemy.orm import Session, exc

from imdb_api import get_film_actors_data, get_film_data
from models import Actor, Film, FilmToActor


def get_db_url() -> str:
    """
    Load environment variables and construct a PostgreSQL connection URL.

    Returns:
        str: The constructed PostgreSQL connection URL.
    """
    load_dotenv()
    pg_vars = ['PG_HOST', 'PG_PORT', 'PG_USER', 'PG_PASSWORD', 'PG_DBNAME']
    credentials = {pg_var: os.environ.get(pg_var) for pg_var in pg_vars}
    return 'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}'.format(
        **credentials,
    )


engine = create_engine(get_db_url(), echo=False)


def session_scalar_where(
    class_object_model,
    class_object_model_field,
    class_object_model_value,
    session: Session,
):
    """
    Execute a scalar query to find the first result where a specified field matches a value.

    Args:
        class_object_model: The SQLAlchemy ORM class representing the table to query.
        class_object_model_field: The field of the class object model to filter by.
        class_object_model_value: The value to match against the specified field.
        session (Session): The current database session.

    Returns:
        Any: The first result that matches the criteria, or None if no match is found.
    """
    return session.scalar(
        select(class_object_model).where(class_object_model_field == class_object_model_value),
    )


def add_film_api(imbd_id: str, session: Session) -> Film | None:
    """
    Add a film to the database if it doesn't exist already.

    Args:
        imbd_id (str): The IMDb ID of the film.
        session (Session): The current database session.

    Returns:
        Film | None: The added film instance or None if the film exists or cannot be added.
    """
    film = session_scalar_where(Film, Film.imbd_id, imbd_id)
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
    """
    Add actors associated with a film to the database.

    Args:
        film_id (Film): The film instance to associate actors with.
        imbd_id (str): The IMDb ID of the film.
        session (Session): The current database session.
    """
    actors_data = get_film_actors_data(imbd_id)
    actors = [Actor(**actor_data) for actor_data in actors_data]
    session.add_all(actors)
    session.flush()
    film_to_actors = [FilmToActor(film_id=film_id, actor_id=actor.id) for actor in actors]
    session.add_all(film_to_actors)
    session.commit()


def create_delete(class_object_model) -> Callable:
    """
    Create a function to delete an class object from the database.

    Args:
        class_object_model: The SQLAlchemy ORM class representing the class object to delete.

    Returns:
        Callable: A function that deletes an class object given its ID.
    """
    def delete_class_object(object_id: UUID, session: Session) -> int | None:
        try:
            class_object = session_scalar_where(
                class_object_model, class_object_model.id, object_id,
            )
            if not class_object:
                return None
            session.delete(class_object)
            session.commit()
            return 1
        except DataError:
            return None
    return delete_class_object


delete_film = create_delete(Film)
delete_actor = create_delete(Actor)


def create_add(class_object_model) -> Callable:
    """
    Create a function to add a new class object to the database.

    Args:
        class_object_model: The SQLAlchemy ORM class representing the class object to add.

    Returns:
        Callable: A function that adds a new class object to the database.
    """
    def create_class_object(class_object_data: dict, session: Session) -> UUID | None:
        try:
            class_object = class_object_model(**class_object_data)
            session.add(class_object)
            session.commit()
            return class_object.id
        except IntegrityError:
            return None
        except ProgrammingError:
            return None
        except DataError:
            return None
    return create_class_object


create_film = create_add(Film)
create_actor = create_add(Actor)


def create_update(class_object_model) -> Callable:
    """
    Create a function to update an existing class object in the database.

    Args:
        class_object_model: The SQLAlchemy ORM class representing the class object to update.

    Returns:
        Callable: A function that updates an class object in the database.
    """
    def update_class_object(new_class_object_data: dict, session: Session):
        try:
            session.bulk_update_mappings(
                class_object_model, [
                    {'id': new_class_object_data['id'], **new_class_object_data},
                ],
            )
            session.commit()
            return new_class_object_data['id']
        except DataError:
            return None
        except exc.StaleDataError:
            return None
        except IntegrityError:
            return None
    return update_class_object


update_film = create_update(Film)
update_actor = create_update(Actor)


def create_get(class_object_model) -> Callable:
    """
    Create a function to retrieve an class object from the database by its ID.

    Args:
        class_object_model: The SQLAlchemy ORM class representing the class object to retrieve.

    Returns:
        Callable: A function that retrieves an class object from the database.
    """
    def get_class_object(class_object_id: dict, session: Session) -> dict | None:
        class_object = session_scalar_where(
            class_object_model, class_object_model.id, class_object_id,
        )
        if not class_object:
            return None
        return class_object.__dict__
    return get_class_object


get_film = create_get(Film)
get_actor = create_get(Actor)


def create_get_all(class_object_model) -> Callable:
    """
    Create a function to retrieve all instances of an class object from the database.

    Args:
        class_object_model: The SQLAlchemy ORM class representing the class objects to retrieve.

    Returns:
        Callable: A function that retrieves all instances of an class object from the database.
    """
    def get_all_class_objects(session: Session) -> list:
        class_objects_data = [
            class_object_model.__dict__ for class_object_model in session.scalars(
                select(class_object_model),
            )
        ]
        for class_object_data in class_objects_data:
            for field, field_value in class_object_data.items():
                if isinstance(field_value, UUID):
                    class_object_data[field] = str(field_value)
        return class_objects_data
    return get_all_class_objects


get_all_films = create_get_all(Film)
get_all_actors = create_get_all(Actor)


def get_film_actors(film_id, session: Session) -> list[dict]:
    """
    Retrieve all actors associated with a film.

    Args:
        film_id: The ID of the film.
        session (Session): The current database session.

    Returns:
        list[dict]: A list of dictionaries representing the actors associated with the film.
    """
    try:
        query = select(Actor).select_from(
            FilmToActor.__table__.join(
                Actor, FilmToActor.actor_id == Actor.id,
            )).where(FilmToActor.film_id == film_id)
        actors = session.scalars(query).all()
    except DataError:
        return None
    if actors:
        return [actor.__dict__ for actor in actors]
    return None
