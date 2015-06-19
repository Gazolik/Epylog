from .model import Player, Game, Weapon, db_session, Kill
from flask import Flask, render_template, make_response
from sqlalchemy import desc, func, and_
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
    # Accessing database for game history
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


@app.route('/gamehistory')
def show_game_history():
    game_history = Game.query.order_by(desc(Game.ending_time))
    return render_template('game_history.html', game_history=game_history)


@app.route('/weapons')
def show_weapon_statistics():
    weapon_list = (db_session.query(
        Weapon.weapon_name.label('weapon_name'),
        func.count(Weapon.weapon_name).label('count'))
                  .join(Weapon.kills)
                  .filter(Kill.player_killer_id != Kill.player_killed_id)
                  .group_by(Weapon.weapon_name)
                  .subquery())
    kill_weapon_player = (db_session.query(
        Kill.weapon_id.label('weapon_id'),
        Kill.player_killer_id.label('player_killer_id'),
        func.count(Kill.weapon_id).label('count'))
        .filter(Kill.player_killer_id != Kill.player_killed_id)
        .group_by(Kill.weapon_id, Kill.player_killer_id)
        .subquery())
    best_kill_weapon = (db_session.query(
        kill_weapon_player.c.weapon_id.label('weapon_id'),
        func.max(kill_weapon_player.c.count).label('maxi'))
        .group_by(kill_weapon_player.c.weapon_id)
        .subquery())

    best_player_weapon = (db_session.query(
        best_kill_weapon.c.maxi.label('kill'),
        Player.pseudo.label('pseudo'),
        Weapon.weapon_name.label('weapon'),
        weapon_list.c.count.label('total'))
        .join(kill_weapon_player, and_(
            kill_weapon_player.c.weapon_id == best_kill_weapon.c.weapon_id,
            kill_weapon_player.c.count == best_kill_weapon.c.maxi))
        .join(Weapon, Weapon.id == kill_weapon_player.c.weapon_id)
        .join(Player, Player.id == kill_weapon_player.c.player_killer_id)
        .join(weapon_list, weapon_list.c.weapon_name == Weapon.weapon_name)
                        )
    return render_template('weapons.html',
                           best_player_weapon=best_player_weapon)


@app.route('/weapons/weapon_graph.svg')
def generate_all_weapons_graph():
    bar_diag = pygal.HorizontalBar()
    bar_diag.title = 'total weapon kills'
    weapon_list = (db_session.query(
        Weapon.weapon_name.label('weapon_name'),
        func.count(Weapon.weapon_name).label('count'))
        .join(Weapon.kills)
        .filter(Kill.player_killer_id != Kill.player_killed_id)
        .group_by(Weapon.weapon_name)
        .order_by(func.count(Weapon.weapon_name)))
    for weapon in weapon_list:
        bar_diag.add(weapon.weapon_name, int(weapon.count))

    svg = bar_diag.render()
    response = make_response(svg)
    response.content_type = 'image/svg+xml'
    return response
