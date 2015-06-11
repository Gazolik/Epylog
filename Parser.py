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
        player_game.game_id = current_game.id
    elif splited_line[0] == "Kill:":
        pass
    elif splited_line[0] == "Item:":
        pass
    elif splited_line[0] == "InitGame:":
        map_name = splited_line[splited_line.index("mapname")+1]
        current_game = Game(map_name=map_name, termination=None)
        s = session()
        s.add(current_game)
        s.commit()
    elif splited_line[0] == "Exit:":
        end = splited_line[1]
        current_game.termination = end;

engine = create_engine('sqlite:///')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


with open('logTest.log', 'r') as f:
    for line in f:
        parse_line(line)
