import datetime

import pyinotify

from .config import file_name
from .model import Game, Player, connection, Kill, Weapon


player_id_matching = {'1022': 'world'}  # (ingame id of player, pseudo)
kills_list = []

weapon_id_matching = {}
weapon_list = connection.query(Weapon).all()
for i in weapon_list:
    weapon_id_matching[i.id] = i


class Parser():
    """
    Class used in order to parse a line from Openarena serverlog file
    """
    def __init__(self):
        self.current_game = Game(map_name=None, termination=None, winner=None)
        try:
            with open('last_date') as last_date:
                self.last_exit = float(last_date.readline())
                print('Last exit: {}'.format(self.last_exit))
        except IOError:
            self.last_exit = 0
            print('Date file doesn\'t exist, reading the whole file')

    def parse(self, line, f):
        """
        Parse a line from the file and put data in database
        """
        splited_line = line.split(' ')
        time = float(splited_line[0])
        if time <= self.last_exit:
            return
        timestamp = datetime.datetime.fromtimestamp(time)
        if splited_line[1] == 'Kill:':
            id_killer = splited_line[2]
            id_killed = splited_line[3]
            id_weapon = splited_line[4][:-1]
            kill = Kill(game=self.current_game, time=timestamp)
            if id_killer == '1022':
                id_killer = id_killed
            kill.player_killer = connection.query(Player).filter(
                Player.pseudo == player_id_matching[id_killer]).first()
            kill.player_killed = connection.query(Player).filter(
                Player.pseudo == player_id_matching[id_killed]).first()
            kill.weapon = weapon_id_matching[int(id_weapon)]
            kills_list.append(kill)
        elif splited_line[1] == 'Item:':
            pass
            # TODO: Add item use, drop
        elif splited_line[1] in ('Rcon', 'InitGame:'):
            connection.rollback()
            kills_list.clear()
            if splited_line[1] == 'Rcon':
                name = splited_line[5][:-1]
            else:
                split_list = line.split('\\')
                name = split_list[split_list.index('mapname')+1]
            self.current_game = Game(
                map_name=name, termination=None, starting_time=timestamp)
            connection.add(self.current_game)
        elif splited_line[1] == 'Exit:':
            end = splited_line[2]
            line = f.readline()
            winner_id = line.split(' ')[8]
            winner = connection.query(Player).filter(
                Player.pseudo == player_id_matching[winner_id]).first()
            self.current_game.winner = winner
            self.current_game.termination = end
            self.current_game.ending_time = timestamp
            for kill in kills_list:
                connection.add(kill)
            connection.commit()
            kills_list.clear()
            with open('last_date', 'w') as last_date:
                last_date.write(splited_line[0])
            self.last_exit = float(splited_line[0])
        elif splited_line[1] == 'ClientUserinfoChanged:':
            ingame_id = splited_line[2]
            name_player = line.split('\\')[1]
            player_id_matching[ingame_id] = name_player
            player = connection.query(Player).filter(
                Player.pseudo == name_player).first()
            if player is None:
                player = Player(pseudo=name_player)
                connection.add(player)
                connection.flush()


parser = Parser()


class EventHandler(pyinotify.ProcessEvent):
    where = 0

    def process_IN_MODIFY(self, event):
        """
        Used when file is modified, if content is erased,
        read from the begining else read from the last update
        """
        with open(file_name) as f:
            f.seek(0, 2)
            if(f.tell() <= self.where):
                self.where = 0
                f.seek(self.where)
            else:
                f.seek(self.where)
                self.where = f.tell()
            for line in f:
                parser.parse(line, f)


wm = pyinotify.WatchManager()
notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
wm.add_watch(file_name, pyinotify.IN_MODIFY, rec=True)

with open(file_name) as f:
    for line in f:
        parser.parse(line, f)
    EventHandler.where = f.tell()
