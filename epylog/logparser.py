from .model import Game, Player, connection, Kill, Weapon
import datetime
import pyinotify
import time
from sqlalchemy.orm import sessionmaker

current_game = Game(map_name=None, termination=None)
player_id_matching = {}  # (id ingame du joueur, pseudo)
player_id_matching['1022'] = 'world'
weapon_id_matching = {}
kills_list = []
lastExit = 0
weapon_list = connection.query(Weapon).all()
for i in weapon_list:
    weapon_id_matching[i.id] = i
try:
    lastDate = open('lastDate', 'r')
    lastExit = float(lastDate.readline())
    print('Last exit : '+str(lastExit))
except IOError:
    lastExit = 0
    print('file doesn t exist')
else:
    lastDate.close()


def parser(line):

    global lastExit
    global current_game
    splited_line = line.split(' ')
    time = float(splited_line[0])
    if(time <= lastExit):
        return
    timestamp = datetime.datetime.fromtimestamp(time)
    if splited_line[1] == 'Kill:':
        id_killer = splited_line[2]
        id_killed = splited_line[3]
        id_weapon = splited_line[4][0:-1]
        kill = Kill()
        kill.game = current_game
        kill.time = timestamp
        if(id_killer == '1022'):
            id_killer = id_killed
        kill.player_killer = connection.query(Player).filter(
                Player.pseudo == player_id_matching[id_killer]).first()
        kill.player_killed = connection.query(Player).filter(
            Player.pseudo == player_id_matching[id_killed]).first()
        kill.weapon = weapon_id_matching[int(id_weapon)]
        kills_list.append(kill)
    elif splited_line[1] == 'Item:':
        id_looter = splited_line[2]
        name_item = splited_line[3][0:-1]
        name_player = player_id_matching[id_looter]
    elif splited_line[1] in ('Rcon', 'InitGame:'):
        connection.rollback()
        kills_list.clear()
        if splited_line[1] == 'Rcon':
            name = splited_line[5][0:-1]
        else:
            split_list = line.split('\\')
            name = split_list[split_list.index('mapname')+1]
        current_game = Game(map_name=name,
                            termination=None, starting_time=timestamp)
        connection.add(current_game)
    elif splited_line[1] == 'Exit:':
        end = splited_line[2]
        print('Exit')
        current_game.termination = end
        current_game.ending_time = timestamp
        for kill in kills_list:
            connection.add(kill)
        connection.commit()
        kills_list.clear()
        player_id_matching['1022'] = 'world'
        with open('lastDate', 'w') as lastDate:
            lastDate.write(splited_line[0])
        lastExit = float(splited_line[0])
    elif splited_line[1] == 'ClientUserinfoChanged:':
        ingame_id = splited_line[2]
        name_player = line.split('\\')[1]
        player_id_matching[ingame_id] = name_player
        player = connection.query(Player).filter(
            Player.pseudo == name_player).first()
        if player is None:
            player = Player(pseudo=name_player)
            connection.add(player)


wm = pyinotify.WatchManager()
file_name = "timeStamp.log"


class EventHandler(pyinotify.ProcessEvent):
    where = 0

    def process_IN_MODIFY(self, event):
                    with open(file_name, 'r') as f:
                        f.seek(0, 2)
                        if(f.tell() <= self.where):
                            self.where = 0
                            f.seek(self.where)
                        else:
                            f.seek(self.where)
                            self.where = f.tell()
                        for line in f:
                            print('nouvelle ligne')
                            parser(line)


notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
notifier.start()
wm.add_watch(file_name, pyinotify.IN_MODIFY, rec=True)

with open(file_name, 'r') as f:
    for line in f:
        parser(line)

    EventHandler.where = f.tell()
