from sqlalchemy import (Column, String, Integer,
                        ForeignKey, create_engine, DateTime)
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy import func, or_
import datetime
from .config import engine_name

Base = declarative_base()


class Player(Base):
    """Represent a player.
    The pseudo of a player is unique.
    """
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String, unique=True)

    @hybrid_method
    def kill_sum(self, date=datetime.datetime.max):
        """Return the number of kills relative to the considered player.
        Suicides are not considered.
        The sum considers kills with a date equal or inferior to the date
        specified in parameter.
        If there is no date specified, all kills are considered.
        """
        return (
            db_session.query(func.count(Kill.player_killed_id))
            .filter_by(player_killer_id=self.id)
            .filter(Kill.player_killer_id != Kill.player_killed_id)
            .filter(Kill.time <= date)
            .group_by(Kill.player_killer_id)
            .scalar())

    @hybrid_method
    def killed_sum(self, date=datetime.datetime.max):
        """Return the number of deaths relative to the considered player.
        Suicides are not considered.
        The sum considers deaths with a date equal or inferior to the date
        specified in parameter.
        If there is no date specified, all deaths are considered.
        """
        return (
            db_session.query(func.count(Kill.player_killer_id))
            .filter_by(player_killed_id=self.id)
            .filter(Kill.player_killer_id != Kill.player_killed_id)
            .filter(Kill.time <= date)
            .group_by(Kill.player_killed_id)
            .scalar())

    @hybrid_method
    def death_sum(self, date=datetime.datetime.max):
        """Return the number of deaths relative to the considered player.
        Suicides are considered.
        The sum considers deaths with a date equal or inferior to the date
        specified in parameter.
        If there is no date specified, all deaths are considered.
        """
        return (
            db_session.query(func.count(Kill.player_killer_id))
            .filter_by(player_killed_id=self.id)
            .filter(Kill.time <= date)
            .group_by(Kill.player_killed_id)
            .scalar())

    @property
    def weapon_statistics(self):
        """Return, for one player, the number of kills with each weapon.
        If the player has never used a weapon, this weapon will not 
        appear in the list.
        """
        return (
            db_session.query(
                Kill.weapon_id,
                func.count(Kill.weapon_id).label('kill_count'))
            .filter_by(player_killer_id=self.id)
            .filter(Kill.player_killed_id != Kill.player_killer_id)
            .group_by(Kill.weapon_id)
            .order_by('kill_count desc')
            .all())

    @property
    def favorite_weapon(self):
        """Return the most used weapon of a player.
        The most used weapon is the weapon with the most number of kills
        associated.
        """
        if self.weapon_statistics:
            return Weapon.query.get(self.weapon_statistics[0][0])

    @property
    def total_game_played(self):
        """Return the total amount of game in wich the player have
        participated.
        Games in which the player has been inactive are not considered.
        """
        return (
            db_session.query(Kill.game_id)
            .filter(or_(
                Kill.player_killer_id == self.id,
                Kill.player_killed_id == self.id))
            .group_by(Kill.game_id)
            .count())

    @property
    def most_killed_player(self):
        """Return the player who the considered player has killed the most.
        """
        return (
            db_session.query(
                Player.pseudo,
                func.count(Kill.player_killed).label('kill_count'))
            .filter(Player.id == Kill.player_killed_id)
            .filter(Kill.player_killer_id == self.id)
            .filter(Kill.player_killer_id != Kill.player_killed_id)
            .group_by(Player.pseudo)
            .order_by('kill_count desc')
            .first())

    @property
    def most_killed_by_player(self):
        """Return the pseudo of the player who the considered player
        has been killed by the most.
        """
        return (
            db_session.query(
                Player.pseudo,
                func.count(Kill.player_killer_id).label('kill_count'))
            .filter(Player.id == Kill.player_killer_id)
            .filter(Kill.player_killed_id == self.id)
            .filter(Kill.player_killer_id != Kill.player_killed_id)
            .group_by(Player.pseudo)
            .order_by('kill_count desc').
            first())

    @hybrid_method
    def kill_list(self, number=None):
        """Return the list of the last players (pseudo) killed by the
        considered player.
        The parameter number limits the number of players returned.
        If there is no number specified, all last players killed are
        considered.
        """
        return [
            p.pseudo for p in (
                db_session.query(Player.pseudo)
                .select_from(Kill)
                .join(Kill.player_killed)
                .filter(Kill.player_killer_id == self.id)
                .order_by(Kill.time.desc())
                .limit(number)
                .all())]

    @hybrid_method
    def killed_list(self, number=None):
        """Return the list of the last players who have killed the considered
        player.
        The parameter number limits the number of players returned.
        If there is no number specified, all last players killer are
        considered.
        """
        return [
            p.pseudo for p in (
                db_session.query(Player.pseudo)
                .select_from(Kill)
                .join(Kill.player_killer)
                .filter(Kill.player_killed_id == self.id)
                .order_by(Kill.time.desc())
                .limit(number)
                .all())]

    @hybrid_method
    def ratio_kill_killed(self, date=datetime.datetime.max):
        """Return the ratio of the player total kills and total deaths.
        Suicides are not considered.
        """
        return round(
            (self.kill_sum(date) or 0) / (self.killed_sum(date) or 1), 2)

    @hybrid_method
    def ratio_kill_death(self, date=datetime.datetime.max):
        """Return the ratio of the player total kills and total deaths.
        Suicides are considered.
        """
        return round(
            (self.kill_sum(date) or 0) / (self.death_sum(date) or 1), 2)

    @property
    def win_number(self):
        """Return the amount of games the considered player have won.
        """
        query = (
            db_session.query(func.count(Game.winner_id).label('count'))
            .group_by(Game.winner_id)
            .having(Game.winner_id == self.id)
            .first())
        return query.count if query is not None else 0


class Kill(Base):
    """Represent a kill.
    """
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
    """Represent a game.
    """
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
        """Return the pseudo of the player who has won the considered game.
        """
        return (
            db_session.query(Player.pseudo)
            .join(Game, Player.id == self.winner_id)
            .first().pseudo)


class Weapon(Base):
    """Represent a weapon.
    """
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    weapon_name = Column(String)
    kills = relationship('Kill', backref='weapon')


engine = create_engine(engine_name)
session = sessionmaker(bind=engine)
connection = session()
Base.metadata.create_all(engine)
connection = session()

db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
Base.query = db_session.query_property()
