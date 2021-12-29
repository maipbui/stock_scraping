import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dataclasses import dataclass, field
from typing import List
import requests

from bs4 import BeautifulSoup
from database.tool import session, engine, Base
from database.ticker import TickerModel


@dataclass
class Price:
    current_price: float
    price_change: float
    price_change_percentage: float


@dataclass
class Ticker:
    name: str
    _company_name: str = field(init=False, default=None)
    _keywords: List[str] = field(init=False, default_factory=list)

    @property
    def price(self):
        url = f"https://cnbc.com/quotes/{self.name}"
        html_content = requests.get(url).text
        doc = BeautifulSoup(html_content, "html.parser")
        last_price_span = doc.find_all("span", {"class": "QuoteStrip-lastPrice"})[0]
        last_price = float(last_price_span.text.replace(",", ""))
        price_change_span = last_price_span.next_sibling.find_all("span")
        price_change = price_change_span[0].text
        if price_change[0] == "+":
            price_change = float(price_change[1:])
        elif price_change[0] == "-":
            price_change = float(price_change[1:]) * (-1)
        else:
            price_change = 0.0

        price_change_percentage: str = (
            price_change_span[1].text.replace("(", " ").replace(")", " ").strip()[:-1]
        )

        if price_change_percentage[0] == "+":
            price_change_percentage = float(price_change_percentage[1:])
        elif price_change_percentage[0] == "-":
            price_change_percentage = float(price_change_percentage[1:]) * (-1)
        else:
            price_change_percentage = 0.0

        price = Price(
            current_price=last_price,
            price_change=price_change,
            price_change_percentage=price_change_percentage,
        )
        return price

    @property
    def company_name(self):
        if self._company_name:
            return self._company_name

        try:
            ticker: TickerModel = (
                session.query(TickerModel).filter(TickerModel.name == self.name).one()
            )
        except Exception as e:
            print("Not Available in db")
        else:
            self._company_name = ticker.company_name
            return self._company_name

        Base.metadata.create_all(engine)
        ticker = TickerModel(name=self.name)
        session.add(ticker)
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        self._company_name = ticker.company_name
        return self._company_name

    @property
    def keywords(self):
        if self._keywords:
            return self._keywords

        try:
            ticker: TickerModel = (
                session.query(TickerModel).filter(TickerModel.name == self.name).one()
            )
        except Exception as e:
            print("Not Available in db")
        else:
            self._keywords = ticker.keywords
            return self._keywords

        Base.metadata.create_all(engine)
        ticker = TickerModel(name=self.name)
        session.add(ticker)
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        self._keywords = ticker.keywords
        return self._keywords


if __name__ == "__main__":
    a = Ticker(name="TSLA")
    print(a.price, a.company_name, a.keywords)
