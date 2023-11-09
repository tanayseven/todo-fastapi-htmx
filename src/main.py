from enum import StrEnum, auto
from typing import Annotated

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.repository import get_db
from src.schema import ListItem

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class State(StrEnum):
    TODO = auto()
    EDIT = auto()
    DONE = auto()


@app.middleware("http")
async def exception_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception:
        return templates.TemplateResponse("dialogs/server_error.html",
                                          {"request": request}, status_code=500)


@app.get("/", response_class=HTMLResponse)
def get_list(request: Request, db: Session = Depends(get_db)):
    todo_list = db.query(ListItem).all()
    if len(todo_list) == 0:
        for item in todo_list:
            db.add(item)
        db.commit()
    return templates.TemplateResponse("index.html", {"request": request, "todo_list": todo_list, "state": State})


@app.delete("/item/{item_id}", response_class=HTMLResponse)
def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    db.query(ListItem).filter(ListItem.id == item_id).delete()
    db.commit()
    todo_list = db.query(ListItem).all()
    print(todo_list)
    return templates.TemplateResponse("list.html", {"request": request, "todo_list": todo_list, "state": State})


@app.get("/item/{item_id}/edit", response_class=HTMLResponse)
def get_edit_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    list_item: ListItem = db.query(ListItem).filter(ListItem.id == item_id).one_or_none()
    if list_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    list_item.state = State.EDIT
    db.commit()
    return templates.TemplateResponse("list_items/edit.html",
                                      {"request": request, "list_item": list_item, "state": State})


@app.patch("/item/{item_id}/edit", response_class=HTMLResponse)
def save_edited_item(request: Request, item_id: int, text: Annotated[str, Form()], db: Session = Depends(get_db)):
    list_item: ListItem = db.query(ListItem).filter(ListItem.id == item_id).one_or_none()
    if list_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    list_item.state = State.TODO
    list_item.text = text
    db.commit()
    return templates.TemplateResponse("list_items/todo.html",
                                      {"request": request, "list_item": list_item, "state": State})


@app.patch("/item/{item_id}/done", response_class=HTMLResponse)
def save_edited_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    list_item: ListItem = db.query(ListItem).filter(ListItem.id == item_id).one_or_none()
    if list_item is None:
        return templates.TemplateResponse("dialogs/item_not_found.html",
                                          {"request": request, "list_item": list_item, "state": State}, status_code=404)
    list_item.state = State.DONE
    db.commit()
    return templates.TemplateResponse("list_items/done.html",
                                      {"request": request, "list_item": list_item, "state": State})


@app.patch("/item/{item_id}/undo", response_class=HTMLResponse)
def undo_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    list_item: ListItem = db.query(ListItem).filter(ListItem.id == item_id).one_or_none()
    if list_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    list_item.state = State.TODO
    db.commit()
    return templates.TemplateResponse("list_items/todo.html",
                                      {"request": request, "list_item": list_item, "state": State})


@app.post("/item/", response_class=HTMLResponse)
def new_item(text: Annotated[str, Form()], request: Request, db: Session = Depends(get_db)):
    new_item = ListItem(
        text=text,
        state=State.TODO,
    )
    db.add(new_item)
    db.commit()
    return templates.TemplateResponse("list_items/todo.html",
                                      {"request": request, "list_item": new_item, "state": State})
