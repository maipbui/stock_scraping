import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.ticker import TickerModel
from abc import ABC, abstractmethod, abstractproperty, abstractproperty
from dataclasses import dataclass, field
from datetime import timedelta
import datetime
from typing import List, Any, Dict

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

from database.news import NewsModel as News
from database.tool import session, Base, engine

import re


class Web_scrapper(ABC):
    @abstractmethod
    def get_news(self) -> Dict[str, List[News]]:
        ...

    @abstractproperty
    def urls(self) -> List[str]:
        ...

    @abstractproperty
    def html_contents(self) -> List[str]:
        ...


def get_driver():
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver


@dataclass
class Webull_scrapper(Web_scrapper):
    ticker_names: List[str]
    ticker_exchanges: List[str]
    scrap_engine: Any = field(init=True, default_factory=lambda: get_driver())

    @property
    def urls(self) -> str:
        return [
            f"https://webull.com/newslist/{ticker_index.lower()}-{ticker_name.lower()}/"
            for ticker_index, ticker_name in zip(
                self.ticker_exchanges, self.ticker_names
            )
        ]

    @property
    def html_contents(self) -> list[str]:
        contents = []
        for url in self.urls:
            if requests.head(url).status_code != 200:
                return []
            self.scrap_engine.get(url)
            contents.append(self.scrap_engine.page_source)
        return contents

    def get_news(self) -> Dict[str, List[News]]:
        news_dict = {}
        for index, html_content in enumerate(self.html_contents):
            news_list: List[News] = []
            doc = BeautifulSoup(html_content, "html.parser")
            news_article_divs = doc.find_all(
                "div", {"class": "wbus13 wbus66 wbus67 wbus70"}
            )
            for div in news_article_divs:
                title = div.find("div", {"class": "wbus14"}).text
                content = (
                    div.find("div", {"class": "wbus20"}).text
                    if div.find("div", {"class": "wbus20"}) is not None
                    else ""
                )
                author = div.find_all("span")[0].text
                timedelta = div.find_all("span")[-1].text
                time_unit: str = timedelta[-5]
                timedelta = int(timedelta[:-5])
                if time_unit.lower() == "d":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        days=timedelta
                    )
                elif time_unit.lower() == "h":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        hours=timedelta
                    )
                elif time_unit.lower() == "m":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        minutes=timedelta
                    )
                elif time_unit.lower() == "s":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        seconds=timedelta
                    )

                news_list.append(
                    News(
                        ticker_name=self.ticker_names[index],
                        title=title,
                        url=self.urls[index],
                        content=content,
                        author=author,
                        created_at=created_at,
                        page="webull",
                        is_new=1,
                    )
                )
            for news in news_list:
                session.add(news)
                try:
                    session.commit()
                except Exception as e:
                    print(e)
                    session.rollback()

            news_dict[self.ticker_names[index].lower()] = news_list

        self.scrap_engine.quit()

        return news_dict


@dataclass
class Reddit_scrapper(Web_scrapper):
    ticker_names: List[str]
    scrap_engine: Any = field(
        init=True,
        default_factory=lambda: get_driver(),
    )

    @property
    def urls(self) -> str:
        return [
            f"https://www.reddit.com/r/wallstreetbets/search/?q={ticker_name}&restrict_sr=1&sr_nsfw=&sort=relevance&t=week"
            for ticker_name in self.ticker_names
        ]

    @property
    def html_contents(self) -> list[str]:
        contents = []
        for url in self.urls:
            if requests.head(url).status_code != 200:
                return []
            self.scrap_engine.get(url)
            contents.append(self.scrap_engine.page_source)
        return contents

    def get_news(self) -> Dict[str, List[News]]:
        news_dict = {}
        for index, html_content in enumerate(self.html_contents):
            news_list: List[News] = []
            doc = BeautifulSoup(html_content, "html.parser")
            posted_by_spans = doc.find_all(
                "span", text=re.compile("Posted[a-z1-9]*", re.IGNORECASE)
            )
            for span in posted_by_spans:
                author = span.next_sibling.text[2:]
                header_div = span.parent.parent
                title_link_div = header_div.find_all("a")[-1]
                url = title_link_div["href"]
                title = (
                    os.path.abspath(title_link_div["href"])
                    .split("/")[-1]
                    .replace("_", " ")
                )
                timedelta = int(title_link_div.text.split(" ")[0])
                time_unit = title_link_div.text.split(" ")[1]
                footer_div = header_div.next_sibling.next_sibling
                upvote = footer_div.find_all("span")[0].text.split(" ")[0]
                comment = footer_div.find_all("span")[1].text.split(" ")[0]
                award = footer_div.find_all("span")[2].text.split(" ")[0]

                if time_unit.lower() == "day" or time_unit.lower() == "days":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        days=timedelta
                    )
                elif time_unit.lower() == "hour" or time_unit.lower() == "hours":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        hours=timedelta
                    )
                elif time_unit.lower() == "minute" or time_unit.lower() == "minutes":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        minutes=timedelta
                    )
                elif time_unit.lower() == "second" or time_unit.lower() == "seconds":
                    created_at = datetime.datetime.now() - datetime.timedelta(
                        seconds=timedelta
                    )

                news_list.append(
                    News(
                        ticker_name=self.ticker_names[index],
                        title=title,
                        content="",
                        url=url,
                        author=author,
                        more_info=f"upvote {upvote}, comment {comment}, award {award}",
                        created_at=created_at,
                        page="reddit",
                        is_new=1,
                    )
                )

            for news in news_list:
                session.add(news)
                try:
                    session.commit()
                except Exception as e:
                    print(e)
                    session.rollback()

            news_dict[self.ticker_names[index].lower()] = news_list

        self.scrap_engine.quit()
        return news_dict


def run(ticker_names: List[str]):
    print("Web: running...")
    ticker_exchanges = []
    for ticker in ticker_names:
        ticker_exchanges.append(
            session.query(TickerModel).filter(TickerModel.name == ticker).one().exchange
        )

    Reddit_scrapper(ticker_names=ticker_names).get_news()

    Webull_scrapper(
        ticker_names=ticker_names, ticker_exchanges=ticker_exchanges
    ).get_news()


if __name__ == "__main__":
    run()
