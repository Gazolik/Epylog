from .model import Player, Game, Weapon, db_session, Kill
from flask import Flask, render_template, make_response
from sqlalchemy import desc, func 
import pygal 

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def home_page():
    top_players = Player.query.all()
    sorted_players = sorted(
        top_players, key=lambda p: p.ratio_kill_killed, reverse=True)
    game_history = Game.query.order_by(desc(Game.ending_time)).limit(5)
    return render_template(
        'home_page.html', 
        top_players=sorted_players[:3],
        game_history=game_history
        )


@app.route('/playerslist')
def show_players_list():
    top_players = Player.query.all()
    sorted_players = sorted(
        top_players, key=lambda p: p.ratio_kill_killed, reverse=True)
    return render_template('player_list.html', top_players=sorted_players)
 

@app.route('/playerdetails/<pseudo>')
def show_player_details(pseudo):
    player = Player.query.filter_by(pseudo=pseudo).first()

    return render_template('player_details.html', player=player)


@app.route('/weapongraph/<pseudo>.svg')
def generate_weapon_graph(pseudo):
    radar_chart = pygal.Radar()
    radar_chart.title = '{} Weapon use'.format(pseudo)
    labels = []
    values = []
    for row in Player.query.filter_by(pseudo=pseudo).first().weapon_statistics:
        labels.append(Weapon.query.get(row[0]).weapon_name)
        values.append(row[1])
    radar_chart.x_labels = labels
    radar_chart.add('Weapon use', values)
    svg = radar_chart.render()
    response = make_response(svg)
    response.content_type = 'image/svg+xml'
    return response


@app.route('/gamehistory')
def show_game_history():
    game_history = Game.query.order_by(desc(Game.ending_time))
    return render_template('game_history.html', game_history=game_history)



@app.route('/weapons')
def show_weapon_statistics():
   weapon_list = (db_session.query(Weapon.weapon_name,func.count(Weapon.weapon_name))
                  .join(Weapon.kills)
                  .filter(Kill.player_killer_id != Kill.player_killed_id)
                  .group_by(Weapon.weapon_name))
   for i in weapon_list:
       print(i[1])
   return render_template('weapons.html', weapon_list = weapon_list)


