from .model import engine, Base, Player, PlayerGame, Game, Kill, Weapon 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from sqlalchemy import func, 

app = Flask(__name__)
app.config.from_object(__name__)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                bind=engine))
Base.query = db_session.query_property()


@app.route('/')
def home_page():
    kills_dict = dict(db_session.query(Player.pseudo, func.count(Kill.player_killed_id).label('kill_sum')).group_by(Player.pseudo).having(Kill.player_killer_id
                    !=
                    Kill.player_killed_id).join(Kill.player_killer).order_by(Player.pseudo))
    deaths_dict = dict(db_session.query(Player.pseudo, func.count(Kill.player_killer_id).label('death_sum')).group_by(Kill.player_killed_id).having(Kill.player_killer_id
                    !=
                    Kill.player_killed_id).join(Kill.player_killed).order_by(Player.pseudo))
    players = db_session.query(Player.pseudo).order_by(Player.pseudo)
    top_players = []
    for player in players:
        nb_kills = 0
        nb_deaths = 1
        if kills_dict.get(player[0]) is not None:
            nb_kills = kills_dict[player[0]]
        if deaths_dict.get(player[0]) is not None:
            nb_deaths = deaths_dict[player[0]]
        top_players.append((player[0], nb_kills, nb_deaths,
            round(nb_kills/nb_deaths, 2)))
    top_players_sorted = sorted(top_players, key=lambda tup: tup[3],
                reverse=True)
    top_players = top_players_sorted[0:3]
    return render_template('home_page.html', top_players=top_players)


@app.route('/playerslist')
def show_players_list():
    #Accessing database for player information (kills, deaths , ratios, ...)
    kills_dict = dict(db_session.query(Player.pseudo, func.count(Kill.player_killed_id).label('kill_sum')).group_by(Player.pseudo).having(Kill.player_killer_id
                    !=
                    Kill.player_killed_id).join(Kill.player_killer).order_by(Player.pseudo))
    deaths_dict = dict(db_session.query(Player.pseudo, func.count(Kill.player_killer_id).label('death_sum')).group_by(Kill.player_killed_id).having(Kill.player_killer_id
                    !=
                    Kill.player_killed_id).join(Kill.player_killed).order_by(Player.pseudo))
    players = db_session.query(Player.pseudo).order_by(Player.pseudo)
    top_players = []
    for player in players:
        nb_kills = 0
        nb_deaths = 1
        if kills_dict.get(player[0]) is not None:
            nb_kills = kills_dict[player[0]]
        if deaths_dict.get(player[0]) is not None:
            nb_deaths = deaths_dict[player[0]]
        top_players.append((player[0], nb_kills, nb_deaths,
            round(nb_kills/nb_deaths, 2)))
    top_players_sorted = sorted(top_players, key=lambda tup: tup[3],
            reverse=True)
    top_players = top_players_sorted
    return render_template('home_page.html', top_players=top_players)
 

@app.route('/playerdetails/<pseudo>')
def show_player_details():
    #Accessing database for game historic
    

    #Route call for weapon graph generation

@app.route('/weapongraph/<pseudo>')
def generate_weapon_graph():
    kill =
    db_session.query(Kill.weapon_id).group_by(Kill.weapon_id).having(player_killer_id=pseudo)
    print(kill)
