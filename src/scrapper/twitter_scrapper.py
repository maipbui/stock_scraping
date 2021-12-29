import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from typing import Any, List
import tweepy
import datetime

from database.news import NewsModel as News
from database.tool import session, Base, engine
from tweepy.models import User
import yaml


def get_client():
    with open("src/resources.yml", "r") as f:
        cfg = yaml.load(f.read(), Loader=yaml.FullLoader)

    ACCESS_TOKEN = cfg["twitter_api"]["ACCESS_TOKEN"]
    ACCESS_TOKEN_SECRET = cfg["twitter_api"]["ACCESS_TOKEN_SECRET"]

    APIKEY = cfg["twitter_api"]["APIKEY"]
    APIKEYSECRET = cfg["twitter_api"]["APIKEYSECRET"]

    BEARER_TOKEN = cfg["twitter_api"]["BEARER_TOKEN"]

    try:
        client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)
    except:
        print("Error during authentication")
        return

    return client


def ticker_scrape(
    following_users: list[User],
    ticket_name: str,
    end_date: str = "now",
):
    if end_date == "now":
        end_date = datetime.datetime.now()
    else:
        end_date = " ".join(end_date, "23:59:59.9999")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")

    start_date = end_date - datetime.timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    news_list: List[News] = []
    client = get_client()
    batch_users_num = 8
    for i in range(0, len(following_users) - batch_users_num, batch_users_num):
        from_str_list = [
            f"from:{following_user.username} OR"
            for following_user in following_users[
                i : min(i + batch_users_num, len(following_users))
            ]
        ]
        from_query = " ".join(from_str_list)[:-3]

        responses = tweepy.Paginator(
            client.search_recent_tweets,
            query=f"${ticket_name} -is:retweet ({from_query})",
            tweet_fields=["created_at"],
            expansions="author_id",
            start_time=start_date,
            end_time=end_date,
            max_results=100,
        )

        for response in responses:
            if response.data:
                for status in response.data:
                    author = client.get_user(id=status.author_id).data
                    url = f"https://twitter.com/{author.username}/status/{status.id}"
                    news_list.append(
                        News(
                            title=f"tweet from {author.name}",
                            url=url,
                            created_at=status.created_at,
                            content=status.text,
                            author=author.username,
                            page="twitter",
                            ticker_name=ticket_name,
                        )
                    )

    for news in news_list:
        session.add(news)
        try:
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()


def run(ticker_names: List[str]):
    print("Twitter: running...")
    client = get_client()
    users = []
    for response in tweepy.Paginator(
        client.get_users_following, id="1367325630476521474", max_results=500
    ):
        users.extend(response[0])

    for ticker in ticker_names:
        ticker_scrape(users, ticker)


if __name__ == "__main__":
    run()
