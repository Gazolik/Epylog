from .model import Player, Game, Weapon, db_session
from flask import Flask, render_template, make_response
from sqlalchemy import desc 
import pygal 

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def home_page():
    top_players = Player.query.all()
    sorted_players = sorted(
        top_players, key=lambda p: p.ratio_kill_killed, reverse=True)
    game_historic = Game.query.order_by(desc(Game.ending_time)).limit(5)
    return render_template(
        'home_page.html', 
        top_players=sorted_players[:3],
        game_historic=game_historic
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
    # Accessing database for game historic
    # Route call for weapon graph generation
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


@app.route('/map_list/')
def show_map_list():
    map_list = db_session.query(Game.map_name).group_by(Game.map_name)
    # interesting stats : -most deadly weapon, avg game duration, 

@app.route('/map_details/<map_name>')
def show_map_details():
    pass
                            
@app.route('/gamehistoric')
def show_game_historic():
    game_historic = Game.query.order_by(desc(Game.ending_time))
    return render_template('game_historic.html', game_historic=game_historic)

@app.route('/weapon')
def show_weapon_statistics():
    pass


