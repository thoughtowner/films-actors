from sqlalchemy import Integer, Float, String, Numeric, Date, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from typing import List

import uuid
import datetime


DEFAULT_IMAGE_POSTER = 'https://img.alicdn.com/imgextra/i4/6000000004704/O1CN01Ine6P81kcTfT3VT2x_!!6000000004704-0-tbvideo.jpg'
DEFAULT_IMAGE_ACTOR = 'https://yourambassadrice.com/wp-content/uploads/2017/12/mNSN76C3QkGGfoD1HbVO_avatar_placeholder-750x750.png'


class Base(DeclarativeBase):
    pass


class IDMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class Film(Base, IDMixin):
    __tablename__ = 'films'

    imbd_id: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column(String, nullable=True)
    imdb_rating: Mapped[float] = mapped_column(Numeric(3, 1), nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    poster: Mapped[str] = mapped_column(nullable=True, default=DEFAULT_IMAGE_POSTER)

    actors: Mapped[List['Actor']] = relationship(back_populates='films')

    __table_args__ = (
        UniqueConstraint('imbd_id', name='film_unique_imbd_id'),
        CheckConstraint("length(title) <= 200"),
        CheckConstraint("imdb_rating >= 0 and imdb_rating <= 10"),
        CheckConstraint("year >= 1895")
    )


class Actor(Base, IDMixin):
    __tablename__ = 'actors'

    imbd_id: Mapped[str] = mapped_column()
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    height: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[str] = mapped_column(String, nullable=True)
    place_of_birth = Mapped[str] = mapped_column(String, nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True, default=DEFAULT_IMAGE_ACTOR)

    films: Mapped[List['Film']] = relationship(back_populates='actors')

    __table_args__ = (
        UniqueConstraint('imbd_id', name='actor_unique_imbd_id'),
        CheckConstraint("length(first_name) <= 100"),
        CheckConstraint("length(last_name) <= 100"),
        CheckConstraint(f"birth_date <= {func.current_date()}")
    )


class FilmToActor(Base):
    __tablename__ = 'film_to_actor'

    film_id: Mapped['Film'] = mapped_column(ForeignKey('films.id', ondelete='cascade'), nullable=True)
    actor_id: Mapped['Actor'] = mapped_column(ForeignKey('actors.id', ondelete='cascade'), nullable=True)

    actor: Mapped['Actor'] = relationship(back_populates='films')
    film: Mapped['Film'] = relationship(back_populates='actors')
