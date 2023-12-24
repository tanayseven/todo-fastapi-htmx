import http
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from returns.result import Success, Failure
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.ext import templates
from src.todo_list.repository import get_all_list_items, delete_list_item, set_state_of_list_item, ItemError, \
    set_text_of_the_list_item
from src.todo_list.schema import State, ListItem
from starlette.requests import Request
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_list(request: Request, db: AsyncSession = Depends(get_db)):
    todo_list = await get_all_list_items(db)
    todo_list = [] if todo_list is None else todo_list
    return templates.TemplateResponse(
        "main.html", {"request": request, "todo_list": todo_list, "state": State}
    )


@router.delete("/item/{item_id}", response_class=HTMLResponse)
async def delete_item(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    await delete_list_item(db, item_id)
    todo_list = await get_all_list_items(db)
    return templates.TemplateResponse(
        "todo-list.html", {"request": request, "todo_list": todo_list, "state": State}
    )


@router.get("/item/{item_id}/edit", response_class=HTMLResponse)
async def get_edit_item(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    list_item_result = await set_state_of_list_item(db, item_id, State.EDIT)
    match list_item_result:
        case Success(list_item):
            return templates.TemplateResponse(
                "list_items/edit.html",
                {"request": request, "list_item": list_item, "state": State},
            )
        case Failure(ItemError.item_not_found):
            return templates.TemplateResponse(
                "dialogs/item_not_found.html",
                {"request": request},
                status_code=http.HTTPStatus.NOT_FOUND.value,
            )


@router.patch("/item/{item_id}/edit", response_class=HTMLResponse)
async def save_edited_item_text(
        request: Request,
        item_id: int,
        text: Annotated[str, Form()],
        db: AsyncSession = Depends(get_db),
):
    list_item_result = await set_text_of_the_list_item(db, item_id, text)
    match list_item_result:
        case Success(list_item):
            return templates.TemplateResponse(
                "list_items/todo.html",
                {"request": request, "list_item": list_item, "state": State},
            )
        case Failure(ItemError.item_not_found):
            return templates.TemplateResponse(
                "dialogs/item_not_found.html",
                {"request": request},
                status_code=http.HTTPStatus.NOT_FOUND.value,
            )
        case Failure(ItemError.item_not_in_edit_state):
            return templates.TemplateResponse(
                "dialogs/item_not_found.html",
                {"request": request},
                status_code=http.HTTPStatus.NOT_FOUND.value,
            )


@router.patch("/item/{item_id}/done", response_class=HTMLResponse)
async def mark_item_as_done(
        request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    list_item_result = await set_state_of_list_item(db, item_id, State.DONE)
    match list_item_result:
        case Success(list_item):
            return templates.TemplateResponse(
                "list_items/done.html",
                {"request": request, "list_item": list_item, "state": State},
            )
        case Failure(ItemError.item_not_found):
            return templates.TemplateResponse(
                "dialogs/item_not_found.html",
                {"request": request},
                status_code=http.HTTPStatus.NOT_FOUND.value,
            )


@router.patch("/item/{item_id}/undo", response_class=HTMLResponse)
async def mark_item_as_undone(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    list_item_result = await set_state_of_list_item(db, item_id, State.TODO)
    match list_item_result:
        case Success(list_item):
            return templates.TemplateResponse(
        "list_items/todo.html",
        {"request": request, "list_item": list_item, "state": State},
    )
        case Failure(ItemError.item_not_found):
            return templates.TemplateResponse(
                "dialogs/item_not_found.html",
                {"request": request},
                status_code=http.HTTPStatus.NOT_FOUND.value,
            )


@router.post("/item/", response_class=HTMLResponse)
async def create_new_item(
        text: Annotated[str, Form()], request: Request, db: AsyncSession = Depends(get_db)
):
    new_item = ListItem(
        text=text,
        state=State.TODO,
    )
    db.add(new_item)
    await db.commit()
    return templates.TemplateResponse(
        "list_items/todo.html",
        {"request": request, "list_item": new_item, "state": State},
    )
