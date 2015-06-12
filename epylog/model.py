from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String)
    player_game = relationship('PlayerGame', backref='player')


class PlayerGame(Base):
    __tablename__ = 'playergame'
    game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)
    player_id = Column(String, ForeignKey('player.id'), primary_key=True)
    kill = Column(Integer)
    death = Column(Integer)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    map_name = Column(String)
    termination = Column(String)
    player_game = relationship('PlayerGame', backref='game')


engine = create_engine('sqlite:////tmp/database')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
connection = session()
