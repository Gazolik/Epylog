from .config import engine_name
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exc

engine = create_engine(engine_name)
session = sessionmaker(bind=engine)
connection = session()
with open('weapon_table.sql', 'r') as f:
    for line in f:
        try:
            connection.execute(line)
        except exc.SQLAlchemyError:
            print('this weapon already exists')
        else:
            connection.commit()
