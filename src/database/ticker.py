from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text

import requests

from .tool import Base, session, engine
import yaml


def get_company_name(context):
    with open("src/resources.yml", "r") as f:
        cfg = yaml.load(f.read(), Loader=yaml.FullLoader)
    ticker_name = context.get_current_parameters()["name"]
    api = cfg["polygon_api"]["API"]
    api_url = (
        f"https://api.polygon.io/v1/meta/symbols/{ticker_name}/company?apiKey={api}"
    )
    company_name = requests.get(api_url).json()["name"]
    return company_name


def get_exchange(context):
    ticker_name = context.get_current_parameters()["name"]
    api = "M7HPSgojI3kTqH2b01fQGUMUSC6DrCcC"
    api_url = (
        f"https://api.polygon.io/v1/meta/symbols/{ticker_name}/company?apiKey={api}"
    )
    exchange = requests.get(api_url).json()["exchangeSymbol"]
    if exchange == "NYE":
        return "NYSE"
    if exchange == "NGS":
        return "NASDAQ"


class TickerModel(Base):
    __tablename__ = "tickers"

    name = Column(String(8), primary_key=True)
    company_name = Column(String(30), nullable=False, default=get_company_name)
    exchange = Column(String(30), nullable=False, default=get_exchange)
    keywords = Column(Text, nullable=True)


# Base = Base.metadata.create_all(engine)
# ticker = Ticker(name="NFLX")
# session.add(ticker)
# session.commit()

# other_ticker = session
