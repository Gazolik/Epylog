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

def parse_line(line, current_game, s):
    splited_line = line.split(' ')
    if splited_line[0] == "ClientConnect:":
        # rajouter joueur dans player_game_list
        print('connection du joueur d id' + splited_line[1])
    elif splited_line[0] == "Kill:":
        id_killer = splited_line[1]
        id_killed = splited_line[2]
        id_weapon = splited_line[3][0:-1]
        # mettre à jour player_game_list
        print('le joueur '+player_id_matching[id_killer]+' a tué'
                +player_id_matching[id_killed]+' avec '+id_weapon)
    elif splited_line[0] == "Item:":
        id_looter = splited_line[1]
        name_item = splited_line[2][0:-1]
        name_player = player_id_matching[id_looter]
        print('le joueur '+name_player+' a trouvé '+name_item)
    elif splited_line[0] in ("Rcon", "InitGame:"):
        s.rollback()
        player_game_list.clear()
        if splited_line[0] == "Rcon":
            map_name = splited_line[4][0:-1]
        else:
            map_name = line.split('\\')[40]
        print('-------------------------------------')
        print('changement de map '+map_name)
        print('-------------------------------------')
        current_game = Game(map_name=map_name, termination=None)
        s.add(current_game)
        s.flush()
    elif splited_line[0] == "Exit:":
        end = splited_line[1]
        current_game.termination = end
        print('-------------------------------------')
        print('fin de la map par:'+end)
        print('-------------------------------------')
        for pseudo, player_game in player_game_list.items():
            s.add(player_game)
            s.flush()
        s.commit()
        player_game_list.clear()
        #player_id_matching.clear()
        player_id_matching['1022'] = 'world'
        # commit tous les player_game de la liste et mettre à jour tous les
        # players
    elif splited_line[0] == "ClientUserinfoChanged:":
        ingame_id = splited_line[1]
        name_player = line.split('\\')[1]
        player_id_matching[ingame_id] = name_player
        player = s.query(Player).filter(Player.pseudo == name_player).first()
        if player is None:
            player = Player(pseudo=name_player)
            s.add(player)
            s.flush()
            print("creation du jouer"+name_player)
        player_game = s.query(PlayerGame).filter(PlayerGame.game_id == current_game.id,
                                                 PlayerGame.player_id == player.id).first()
        if player_game is None:
            player_game = PlayerGame(kill=0)
            player_game.player = player
            player_game.game = current_game
            player_game_list[player.pseudo] = player_game
        print('l id de '+name_player+' est '+ingame_id)
    elif splited_line[0] == "ClientDisconnect:":
        print('le joueur '+player_id_matching[splited_line[1][0:-1]]+' s est deconnecté')
        del player_id_matching[splited_line[1][0:-1]]
engine = create_engine('sqlite:///')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

s = session()
with open('logTest.log', 'r') as f:
    for line in f:
        parse_line(line, current_game, s)
