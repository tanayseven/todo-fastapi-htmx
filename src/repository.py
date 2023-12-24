from enum import StrEnum, auto
from typing import Sequence

from returns.result import Result, Success, Failure
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.schema import ListItem, State


class ItemError(StrEnum):
    item_not_found = auto()
    item_not_in_edit_state = auto()


async def get_all_list_items(db: AsyncSession) -> Sequence[ListItem]:
    query = select(ListItem)
    return (await db.execute(query)).scalars().all()


async def delete_list_item(db: AsyncSession, item_id: int):
    query = delete(ListItem).where(ListItem.id == item_id)
    await db.execute(query)
    await db.commit()


async def set_state_of_list_item(db: AsyncSession, item_id: int, state: State) -> Result[ItemError, ListItem]:
    query = select(ListItem).where(ListItem.id == item_id)
    list_item = (await db.execute(query)).scalars().one_or_none()
    if list_item is None:
        return Failure(ItemError.item_not_found)
    list_item.state = state
    await db.commit()
    return Success(list_item)


async def set_text_of_the_list_item(db: AsyncSession, item_id: int, text: str) -> Result[ItemError, ListItem]:
    query = select(ListItem).where(ListItem.id == item_id)
    list_item = (await db.execute(query)).scalars().one_or_none()
    if list_item is None:
        return Failure(ItemError.item_not_found)
    if list_item.state != State.EDIT:
        return Failure(ItemError.item_not_in_edit_state)
    list_item.state = State.TODO
    list_item.text = text
    await db.commit()
    return Success(list_item)
