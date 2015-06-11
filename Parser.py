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

class PlayerGame(Base):
    __tablename__ = 'playerGame'
    game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)
    player = Column(String, ForeignKey('player.id'), primary_key=True)
    kill = Column(Integer)

class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    map_name = Column(String)
    termination = Column(String)

current_game = None

def parse_line(line):
    splited_line = line.split(' ')
    if splited_line[0] == "ClientConnect:":
        client_info = f.readline().split('\\')
        player_game = PlayerGame(kill=1)
	print('connection du joueur' + client_info[1])
        player_game.game_id = current_game.id
    elif splited_line[0] == "Kill:":
        nomTueur = splited_line[4]
        nomTue = splited_line[6]
        arme = splited_line[8]
        print('le joueur '+nomTueur+' a tué '+nomTue+' avec '+arme)
    elif splited_line[0] == "Item:":
        idLooter = splited_line[1]
        nomItem = splited_line[2]
        for i in joueurs:
            if joueurs[i] == idLooter:
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
        print('-------------------------------------')
        print('fin de la map par:'+end)
        print('-------------------------------------')
        
	current_game.termination = end;
    elif splited_line[0] == "ClientUserinfoChanged:":
        id = splited_line[1]
        name = splited_line[2].split('\\')[1]
        joueurs[name]=id
        print('l id de '+name+' est '+id)

engine = create_engine('sqlite:///')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


with open('logTest.log', 'r') as f:
    for line in f:
        parse_line(line)
