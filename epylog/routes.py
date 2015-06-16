from flask import Flask
from .model import engine, Base, Player, PlayerGame, Game
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from sqlalchemy import func, Float

app = Flask(__name__)
app.config.from_object(__name__)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = db_session.query_property()


@app.route('/')
def home_page():
    players = db_session.query(PlayerGame.player_id, Player.pseudo,
            func.sum(PlayerGame.kill).label('kill_sum'),
            func.sum(PlayerGame.death).label('death_sum'),
            func.round((func.sum(func.cast(PlayerGame.kill,
                Float))/func.sum(PlayerGame.death)), 2).label('ratio')).group_by(PlayerGame.player_id).order_by('ratio desc').join(PlayerGame.player)[0:3]
    return render_template('home_page.html', players=players)


@app.route('/playerslist')
def show_players_list():
    players = db_session.query(Player).all()
    return render_template('home_page.html', players=players)


@app.route('/playerdetails')
def show_player_details():
    pass
