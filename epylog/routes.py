from flask import Flask
from .model import engine, Base, Player, PlayerGame, Game
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


app = Flask(__name__)
app.config.from_object(__name__)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = db_session.query_property()

@app.route('/')
def home_page():
    players = Player.query.all()
    return render_template('home_page.html', players=players)

@app.route('/playerslist')
def show_players_list():
    players = Player.query.all()
    return render_template('home_page.html', players=players)

