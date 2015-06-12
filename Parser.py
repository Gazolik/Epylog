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
player_id_matching = {}   # (pseudo, id ingame du joueur)


def parse_line(line, current_game):
    splited_line = line.split(' ')
    if splited_line[0] == "ClientConnect:":
        client_info = f.readline().split('\\')
        s = session()
        player = s.query(Player).filter(Player.pseudo ==
                    client_info[1]).first()
        if player is None:
            player = Player(pseudo=client_info[1])
            s.add(player)
            s.commit()
            
        else:
            player_game = PlayerGame(kill=0)
            print(player)
            player_game.player = player
            player_game.game = current_game
        
        player_game_list[player.pseudo] = player_game
        
        print('connection du joueur'+client_info[1])
        # rajouter joueur dans player_game_list
    elif splited_line[0] == "Kill:":
        nom_tueur = splited_line[4]
        nom_tue = splited_line[6]
        arme = splited_line[8]
        # mettre à jour player_game_list
        print('le joueur '+nomTueur+' a tué '+nomTue+' avec '+arme)
    elif splited_line[0] == "Item:":
        idLooter = splited_line[1]
        nomItem = splited_line[2]
        for i in player_id_matching:
            if player_id_matching[i] == idLooter:
                nomjoueur = i
                print('le joueur '+nomjoueur+' a trouvé '+nomItem)
                break
    elif splited_line[0] == "Rcon":
        Init = splited_line[3].split('\\')
        print('-------------------------------------')
        print('changement de map '+splited_line[4])
        print('-------------------------------------')
        map_name = splited_line[4]
        current_game = Game(map_name=map_name, termination=None)
        s = session()
        s.add(current_game)
        s.commit()
    elif splited_line[0] == "Exit:":
        end = splited_line[1]
        current_game.termination = end;
        print('-------------------------------------')
        print('fin de la map par:'+end)
        print('-------------------------------------')
        # commit tous les player_game de la liste et mettre à jour tous les
        # players
    elif splited_line[0] == "ClientUserinfoChanged:":
        ingame_id = splited_line[1]
        pseudo = splited_line[2].split('\\')[1]
        player_id_matching[pseudo]=ingame_id
        print('l id de '+name+' est '+ingame_id)

engine = create_engine('sqlite:///')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


with open('logTest.log', 'r') as f:
    for line in f:
        parse_line(line, current_game)
