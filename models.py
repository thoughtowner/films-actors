from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from typing import List

import uuid
from datetime import date
from typing import Optional


# DEFAULT_IMAGE_POSTER = 'https://img.alicdn.com/imgextra/i4/6000000004704/O1CN01Ine6P81kcTfT3VT2x_!!6000000004704-0-tbvideo.jpg'
DEFAULT_IMAGE_POSTER = 'https://eloutput.com/wp-content/uploads/2022/03/imagen-geometria-proyector.png'
# DEFAULT_IMAGE_ACTOR = 'https://yourambassadrice.com/wp-content/uploads/2017/12/mNSN76C3QkGGfoD1HbVO_avatar_placeholder-750x750.png'
# DEFAULT_IMAGE_ACTOR = 'https://bogatyr.club/uploads/posts/2023-03/1679614430_bogatyr-club-p-chernii-fon-feisit-vkontakte-72.jpg'
DEFAULT_IMAGE_ACTOR = 'https://static10.tgstat.ru/channels/_0/1a/1affec596ab6b9a4dc2003870012508a.jpg'


class Base(DeclarativeBase):
    pass


class IDMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class Film(Base, IDMixin):
    __tablename__ = 'films'

    imbd_id: Mapped[str] = mapped_column()
    title: Mapped[Optional[str]] = mapped_column(nullable=True)
    imdb_rating: Mapped[Optional[float]] = mapped_column(nullable=True)
    year: Mapped[Optional[int]] = mapped_column(nullable=True)
    poster: Mapped[Optional[str]] = mapped_column(nullable=True, default=DEFAULT_IMAGE_POSTER)
    country: Mapped[Optional[str]] = mapped_column(nullable=True)

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
    full_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    height: Mapped[Optional[str]] = mapped_column(nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(nullable=True, default=DEFAULT_IMAGE_ACTOR)
    birth_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    place_of_birth: Mapped[Optional[str]] = mapped_column(nullable=True)

    films: Mapped[List['Film']] = relationship(back_populates='actors')

    __table_args__ = (
        UniqueConstraint('imbd_id', name='actor_unique_imbd_id'),
        CheckConstraint("length(full_name) <= 200")
        # CheckConstraint(f"{birth_date} <= {func.current_date()}")
    )


class FilmToActor(Base, IDMixin):
    __tablename__ = 'film_to_actor'

    film_id: Mapped['Film'] = mapped_column(ForeignKey('films.id', ondelete='cascade'), nullable=True)
    actor_id: Mapped['Actor'] = mapped_column(ForeignKey('actors.id', ondelete='cascade'), nullable=True)
    # character: Mapped[str] = mapped_column(nullable=True)

    actor: Mapped['Actor'] = relationship(back_populates='films')
    film: Mapped['Film'] = relationship(back_populates='actors')
