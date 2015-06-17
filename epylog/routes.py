from .model import engine, Base, Player, PlayerGame, Game, Kill, Weapon, db_session
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from sqlalchemy import func 

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def home_page():
    top_players = Player.query.all()
    sorted_players = sorted(
        top_players, key=lambda p: p.ratio_kill_killed, reverse=True)
    return render_template('home_page.html', top_players=sorted_players[:3])


@app.route('/playerslist')
def show_players_list():
    top_players = Player.query.all()
    sorted_players = sorted(
        top_players, key=lambda p: p.ratio_kill_killed, reverse=True)
    return render_template('home_page.html', top_players=sorted_players)
 

@app.route('/playerdetails/<pseudo>')
def show_player_details(pseudo):
    player = Player.query.filter_by(pseudo=pseudo).first()
    # Accessing database for game historic
    # Route call for weapon graph generation
    return render_template('player_details.html', player=player)


@app.route('/weapongraph/<pseudo>')
def generate_weapon_graph(pseudo):
    kill = db_session.query(Kill.weapon_id).group_by(Kill.weapon_id).having(player_killer_id=pseudo)
    print(kill)
