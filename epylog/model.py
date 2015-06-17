from sqlalchemy import (Column, String, Integer,
                        ForeignKey, create_engine, DateTime)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String)


class Kill(Base):
    __tablename__ = 'kill'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    player_killer_id = Column(Integer, ForeignKey('player.id'))
    player_killer = relationship('Player', foreign_keys=[player_killer_id])
    player_killed_id = Column(Integer, ForeignKey('player.id'))
    player_killed = relationship('Player', foreign_keys=[player_killed_id])
    weapon_id = Column(Integer, ForeignKey('weapon.id'))
    time = Column(DateTime)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    map_name = Column(String)
    termination = Column(String)
    kills = relationship('Kill', backref='game')
    starting_time = Column(DateTime)
    ending_time = Column(DateTime)


class Weapon(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    weapon_name = Column(String)
    kills = relationship('Kill', backref='weapon')

engine = create_engine('sqlite:////tmp/database')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
connection = session()
