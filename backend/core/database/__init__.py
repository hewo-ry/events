import uuid
import datetime
from typing import Any
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.orm import sessionmaker, declared_attr, declarative_mixin
from sqlalchemy.ext.declarative import as_declarative

from core.database.types import GUID
from config import settings

SQLALCHEMY_DATABASE_URL = "postgresql://{username}:{password}@{server}/{db}".format(
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    server=settings.DATABASE_SERVER,
    db=settings.DATABASE_NAME,
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def timezoned() -> datetime.datetime:
    return datetime.datetime.now().astimezone(settings.TIME_ZONE)


@as_declarative()
class Base:
    id: Any
    __name__: str


@declarative_mixin
class ObjectMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __mapper_args__ = {"always_refresh": True}

    uuid = Column(GUID(), primary_key=True, default=uuid.uuid4)
    created_on = Column(DateTime, default=timezoned)
    updated_on = Column(DateTime, nullable=True)
