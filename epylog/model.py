from sqlalchemy import (Column, String, Integer,
                        ForeignKey, create_engine, DateTime)
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, or_
from .config import engine_name as engine_name

Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String, unique=True)

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
    def weapon_statistics(self):
        return (
            db_session
            .query(Kill.weapon_id,
                   func.count(Kill.weapon_id).label('kill_count'))
            .filter_by(player_killer_id=self.id)
            .filter(Kill.player_killed_id != Kill.player_killer_id)
            .group_by(Kill.weapon_id)
            .order_by('kill_count desc')
            .all()
            )

    def favorite_weapon(self):
        if self.weapon_statistics:
            return Weapon.query.get(self.weapon_statistics[0][0])
        else:
            return None

    @hybrid_property
    def total_game_played(self):
        return (
            Kill.query
            .filter(or_(Kill.player_killer_id == self.id,
                        Kill.player_killed_id == self.id))
            .group(Kill.game_id)
            .count()
            )

    def most_killed_player(self):
        player = (
                db_session
                .query(Kill.player_killed_id,
                       func.count(Kill.player_killed_id).label('kill_count'))
                .filter_by(player_killer_id=self.id)
                .filter(Kill.player_killer_id != Kill.player_killed_id)
                .group_by(Kill.player_killed_id)
                .order_by('kill_count desc').first()
                )
        if player:
            return Player.query.get(player[0])
        else:
            return None

    def most_killed_by_player(self):
        player = (
                db_session
                .query(Kill.player_killer_id,
                       func.count(Kill.player_killer_id).label('kill_count'))
                .filter_by(player_killed_id=self.id)
                .filter(Kill.player_killer_id != Kill.player_killed_id)
                .group_by(Kill.player_killer_id)
                .order_by('kill_count desc').first()
                )
        if player:
            return Player.query.get(player[0])
        else:
            return None

    def kill_list(self, number=None):
        return [p.pseudo for p in (
            db_session
            .query(Player.pseudo)
            .select_from(Kill)
            .join(Kill.player_killed)
            .filter(Kill.player_killer_id == self.id)
            .order_by(Kill.time.desc())
            .limit(number)
            .all())
            ]

    def killed_list(self, number=None):
        return [p.pseudo for p in (
            db_session
            .query(Player.pseudo)
            .select_from(Kill)
            .join(Kill.player_killer)
            .filter(Kill.player_killed_id == self.id)
            .order_by(Kill.time.desc())
            .limit(number)
            .all())
            ]

    @property
    def ratio_kill_killed(self):
        return round((self.kill_sum or 0) / (self.killed_sum or 1), 2)

    @property
    def ratio_kill_death(self):
        return round((self.kill_sum or 0) / (self.death_sum or 1), 2)

    def win_number(self):
        query = (db_session.query(func.count(Game.winner_id))
                 .group_by(Game.winner_id)
                 .having(Game.winner_id == self.id)
                 .first())
        if query is not None:
            return query[0]
        else:
            return 0


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
    winner_id = Column(Integer, ForeignKey('player.id'))
    winner = relationship('Player', foreign_keys=[winner_id])

    def winner_name(self):
        return (db_session.query(Player.pseudo)
                .join(Game, Player.id == self.winner_id).first()[0])


class Weapon(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    weapon_name = Column(String)
    kills = relationship('Kill', backref='weapon')


engine = create_engine(engine_name)
session = sessionmaker(bind=engine)
connection = session()
Base.metadata.create_all(engine)
connection = session()

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()
