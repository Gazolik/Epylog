from sqlalchemy import (Column, String, Integer,
                        ForeignKey, create_engine, DateTime)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from operator import itemgetter

Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String)
    player_game = relationship('PlayerGame', backref='player')
    
    @hybrid_property
    def kill_sum(self):
        return (
            db_session
            .query(func.count(Kill.player_killed_id))
            .filter_by(player_killer_id=self.id)
            .filter(Kill.player_killer_id != Kill.player_killed_id)
            .group_by(Kill.player_killer_id)
            .scalar()
            )

    @hybrid_property
    def killed_sum(self):
        return (
            db_session
            .query(func.count(Kill.player_killer_id))
            .filter_by(player_killed_id=self.id)
            .filter(Kill.player_killer_id != Kill.player_killed_id)
            .group_by(Kill.player_killed_id)
            .scalar()
            )

    @hybrid_property
    def death_sum(self):
        return (
            db_session
            .query(func.count(Kill.player_killer_id))
            .filter_by(player_killed_id=self.id)
            .group_by(Kill.player_killed_id)
            .scalar()
            )

    @hybrid_property
    def weapon_statitics(self):
        return (
            db_session
            .query(Kill.weapon_id, func.count(Kill.weapon_id))
            .filter_by(player_killed_id=self.id)
            .group_by(Kill.weapon_id)
            )

    @hybrid_property
    def favorite_weapon(self):
        w_id = max(self.weapon_statistic, key=itemgetter(1))[0]
        return Weapon.query.filter(id=w_id).one()

    @property
    def ratio_kill_killed(self):
        return round((self.kill_sum or 0) / (self.killed_sum or 1), 2)
 
    @property
    def ratio_kill_death(self):
        return round((self.kill_sum or 0) / (self.death_sum or 1), 2)
    

        

class PlayerGame(Base):
    __tablename__ = 'playergame'
    game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    kill = Column(Integer)
    death = Column(Integer)
    score = Column(Integer)



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

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                bind=engine))
Base.query = db_session.query_property()


