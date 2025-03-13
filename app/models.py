from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship 
from sqlalchemy import ForeignKey, String, Integer, Boolean, Table
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

invites = Table(
    "event_invites",
    Base.metadata,
    db.Column("player_id", db.ForeignKey("player.id")),
    db.Column("event_id", db.ForeignKey("event.id"))
)

class Account(Base):
    __tablename__ = 'account'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    player: Mapped['Player'] = relationship(back_populates='account', uselist=False)

class Player(Base):
    __tablename__ = 'player'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    picture: Mapped[str] = mapped_column(String, nullable=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('account.id'))

    owned_events: Mapped[list['Event']] = relationship(back_populates='owner')
    account: Mapped['Account'] = relationship(back_populates='player')
    event_players: Mapped[list['EventPlayers']] = relationship(back_populates='player')
    player_scores: Mapped[list['PlayerScore']] = relationship(back_populates='player')
    invites: Mapped[list['Event']] = relationship(secondary="event_invites", back_populates='invites')

class Event(Base):
    __tablename__ = 'event'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey('player.id'))

    owner: Mapped['Player'] = relationship(back_populates='owned_events')
    rounds: Mapped[list['Round']] = relationship(back_populates='event')
    event_players: Mapped[list['EventPlayers']] = relationship(back_populates='event')
    invites: Mapped[list['Player']] = relationship(secondary="event_invites", back_populates='invites')

class Round(Base):
    __tablename__ = 'round'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey('event.id'))

    event: Mapped['Event'] = relationship(back_populates='rounds')
    player_scores: Mapped[list['PlayerScore']] = relationship(back_populates='round')

class PlayerScore(Base):
    __tablename__ = 'player_score'

    player_id: Mapped[int] = mapped_column(ForeignKey('player.id'), primary_key=True)
    round_id: Mapped[int] = mapped_column(ForeignKey('round.id'), primary_key=True)

    hole_scores = {f'hole_{i}': mapped_column(Integer) for i in range(1, 19)}
    total: Mapped[int] = mapped_column(Integer)

    player: Mapped['Player'] = relationship(back_populates='player_scores')
    round: Mapped['Round'] = relationship(back_populates='player_scores')

class EventPlayers(Base):
    __tablename__ = 'event_players'

    player_id: Mapped[int] = mapped_column(ForeignKey('player.id'), primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('event.id'), primary_key=True)

    event_score: Mapped[int] = mapped_column(Integer)

    player: Mapped['Player'] = relationship(back_populates='event_players')
    event: Mapped['Event'] = relationship(back_populates='event_players')

class Course(Base):
    __tablename__ = 'course'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    par: Mapped[int] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String)



