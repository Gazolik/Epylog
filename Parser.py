from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String)
    player_game = relationship("PlayerGame", backref="player")


class PlayerGame(Base):
    __tablename__ = 'playerGame'
    game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)
    player_id = Column(String, ForeignKey('player.id'), primary_key=True)
    kill = Column(Integer)
    death = Column(Integer)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    map_name = Column(String)
    termination = Column(String)
    player_game = relationship("PlayerGame", backref="game")

current_game = Game(map_name=None, termination=None)
player_game_list = {}  # (pseudo, player_game)
player_id_matching = {}  # (id ingame du joueur, pseudo)
player_id_matching['1022'] = 'world'

engine = create_engine('sqlite:///database')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s = session()

with open('logTest.log', 'r') as f:
    for line in f:
        splited_line = line.split(' ')
        if splited_line[0] == "ClientConnect:":
            print('connection du joueur d id' + splited_line[1])
        elif splited_line[0] == "Kill:":
            id_killer = splited_line[1]
            id_killed = splited_line[2]
            id_weapon = splited_line[3][0:-1]
            print('le joueur '+player_id_matching[id_killer]+' a tué'+
                   player_id_matching[id_killed]+' avec '+id_weapon)
            if id_killer != id_killed and id_killer != '1022':
                player_game_list[player_id_matching[id_killer]].kill += 1
            player_game_list[player_id_matching[id_killed]].death += 1
        elif splited_line[0] == "Item:":
            id_looter = splited_line[1]
            name_item = splited_line[2][0:-1]
            name_player = player_id_matching[id_looter]
            print('le joueur '+name_player+' a trouvé '+name_item)
        elif splited_line[0] in ("Rcon", "InitGame:"):
            s.rollback()
            player_game_list.clear()
            if splited_line[0] == "Rcon":
                name = splited_line[4][0:-1]
            else:
                split_list = line.split('\\')
                name = split_list[split_list.index("mapname")+1]
            print('-------------------------------------')
            print('changement de map '+name)
            print('-------------------------------------')
            current_game = Game(map_name=name, termination=None)
            s.add(current_game)
        elif splited_line[0] == "Exit:":
            end = splited_line[1]
            current_game.termination = end
            print('-------------------------------------')
            print('fin de la map par:'+end)
            print('-------------------------------------')
            for pseudo, player_game in player_game_list.items():
                s.add(player_game)
            s.commit()
            player_game_list.clear()
            player_id_matching['1022'] = 'world'
        elif splited_line[0] == "ClientUserinfoChanged:":
            ingame_id = splited_line[1]
            name_player = line.split('\\')[1]
            player_id_matching[ingame_id] = name_player
            player = s.query(Player).filter(Player.pseudo == name_player).first()
            if player is None:
                player = Player(pseudo=name_player)
                s.add(player)
                print("creation du jouer"+name_player)
            player_game = s.query(PlayerGame).filter(PlayerGame.game == current_game,
                                                 PlayerGame.player == player).first()
            if player_game is None:
                player_game = PlayerGame(kill=0, death=0)
                player_game.player = player
                player_game.game = current_game
                player_game_list[player.pseudo] = player_game
            print('l id de '+name_player+' est '+ingame_id)
        elif splited_line[0] == "ClientDisconnect:":
            print('le joueur '+player_id_matching[splited_line[1][0:-1]]+' s est deconnecté')
            del player_id_matching[splited_line[1][0:-1]]
