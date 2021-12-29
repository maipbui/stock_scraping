from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml


def get_db_tools():
    with open("src/resources.yml", "r") as f:
        cfg = yaml.load(f.read(), Loader=yaml.FullLoader)
    username = cfg["database"]["username"]
    password = cfg["database"]["password"]
    Session = sessionmaker()
    engine = create_engine(
        f"mysql+mysqlconnector://{username}:{password}@localhost/webscrapper",
        echo=False,
    )
    Session.configure(bind=engine)
    session = Session()
    return session, engine


session, engine = get_db_tools()
Base = declarative_base()
