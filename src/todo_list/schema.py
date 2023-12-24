from dataclasses import dataclass
from enum import StrEnum, auto

from sqlalchemy import Column, Integer, String

from src.database import Base


class State(StrEnum):
    TODO = auto()
    EDIT = auto()
    DONE = auto()


@dataclass
class ListItem(Base):
    __tablename__ = "list_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    state = Column(String, nullable=False)
