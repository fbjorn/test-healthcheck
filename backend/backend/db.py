from datetime import datetime
from typing import List, Tuple, Type, TypeVar

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

Base = declarative_base()

BM = TypeVar("BM", bound="BaseDBModel")


class BaseDBModel(Base):  # type: ignore
    __abstract__ = True

    id = Column(Integer, primary_key=True)  # noqa: A003

    def save_to_db(self):
        session.add(self)
        session.commit()

    @classmethod
    def list_all(cls: Type[BM]) -> List[BM]:
        return session.query(cls).all()  # type: ignore

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.__class__.__name__)


class ServiceStatus(BaseDBModel):
    __tablename__ = "service_status"

    code = Column(Integer, nullable=False)
    elapsed = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow())
    url = Column(String, nullable=False)

    def __str__(self):
        return f"<{self.url} [{self.code}] {self.date}>"


def create_session(connection_string: str) -> Tuple[Session, Engine]:
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)(), engine


def create_tables(settings):
    for db in settings.databases:
        create_session(f"postgresql://root:root@db/{db}")


session, _ = create_session("postgresql://root:root@db/healthcheck")
