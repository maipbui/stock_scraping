from sqlalchemy import create_engine, func
from sqlalchemy.orm import declarative_base, session, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

from typing import Optional, Tuple

from dataclasses import dataclass, field
import datetime
from urllib.parse import urlparse
import hashlib

from .tool import Base


def get_hash(context):
    content = context.get_current_parameters()["content"]
    short_content = (
        context.get_current_parameters()["content"][:20]
        if (len(content) > 20)
        else context.get_current_parameters()["content"]
    )
    ticker_name = context.get_current_parameters()["ticker_name"]
    created_at = context.get_current_parameters()["created_at"]
    author = context.get_current_parameters()["author"]
    string = ticker_name + short_content + author
    val = int(hashlib.sha256(string.encode("utf-8")).hexdigest(), 16) % (10 ** 5)
    val = str(str(val) + created_at.strftime("%m%d"))
    print("hash...", val)
    return val


class NewsModel(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    ticker_name = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    url = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    author = Column(String(50), nullable=False)
    author_Karma = Column(Integer, nullable=True)
    more_info = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    retrieved_at = Column(DateTime, default=func.now())
    hash_val = Column(String(20), default=get_hash, unique=True, onupdate=get_hash)
    page = Column(String(100), nullable=False)
    is_new = Column(Boolean, nullable=True)

    @property
    def short_content(self):
        limit = 30
        if len(self.content) > limit:
            return self.content[:limit] + "..."
        else:
            return self.content

    @property
    def domain_name(self):
        parse = urlparse(self.url)
        return parse.netloc
