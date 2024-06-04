"""Module for table models in the database."""


import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

POSTER_IMAGE = 'https://eloutput.com/wp-content/uploads/2022/03/imagen-geometria-proyector.png'
ACTOR_IMAGE = 'https://static10.tgstat.ru/channels/_0/1a/1affec596ab6b9a4dc2003870012508a.jpg'


class Base(DeclarativeBase):
    """Base class for tables."""

    pass


class IDMixin:
    """Mixin class for the field id."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class Film(Base, IDMixin):
    """Class for the table films."""

    __tablename__ = 'films'

    imdb_id: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[Optional[str]] = mapped_column()
    imdb_rating: Mapped[Optional[float]] = mapped_column(nullable=True)
    year: Mapped[Optional[int]] = mapped_column(nullable=True)
    poster: Mapped[Optional[str]] = mapped_column(nullable=True, default=POSTER_IMAGE)
    country: Mapped[Optional[str]] = mapped_column(nullable=True)

    actors: Mapped[List['Actor']] = relationship(
        'Actor', secondary='film_to_actor', back_populates='films',
    )

    __table_args__ = (
        UniqueConstraint('imdb_id', name='film_unique_imdb_id'),
        CheckConstraint('length(title) <= 200', name='title_length_less_than_or_equal_200'),
        CheckConstraint(
            'imdb_rating >= 0 and imdb_rating <= 10',
            name='imdb_rating_more_than_or_equal_0_and_less_than_or_equal_10',
        ),
        CheckConstraint('year >= 1895', name='year_more_than_or_equal_1895'),
    )


class Actor(Base, IDMixin):
    """Class for the table actors."""

    __tablename__ = 'actors'

    imdb_id: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column()
    height: Mapped[Optional[str]] = mapped_column(nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(nullable=True, default=ACTOR_IMAGE)
    birth_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    place_of_birth: Mapped[Optional[str]] = mapped_column(nullable=True)

    films: Mapped[List['Film']] = relationship(
        'Film', secondary='film_to_actor', back_populates='actors',
    )

    __table_args__ = (
        UniqueConstraint('imdb_id', name='actor_unique_imdb_id'),
        CheckConstraint('length(full_name) <= 200'),
        CheckConstraint('birth_date <= CURRENT_DATE', name='check_birth_date'),
    )


class FilmToActor(Base, IDMixin):
    """Class for the table film_to_actor."""

    __tablename__ = 'film_to_actor'

    film_id: Mapped['Film'] = mapped_column(
        ForeignKey('films.id', ondelete='cascade'),
        nullable=True,
    )
    actor_id: Mapped['Actor'] = mapped_column(
        ForeignKey('actors.id', ondelete='cascade'),
        nullable=True,
    )
    character: Mapped[str] = mapped_column(nullable=True)
