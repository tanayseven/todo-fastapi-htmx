from typing import Annotated

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

todo_list = [
    dict(id=1, text="Buy Milk", state="DONE"),
    dict(id=2, text="Clean the room", state="TODO"),
    dict(id=3, text="Do the laundry", state="TODO"),
    dict(id=4, text="Buy Eggs", state="DONE"),
    dict(id=5, text="Write blog post", state="TODO"),
]


@app.get("/")
def get_list(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "todo_list": todo_list})


@app.delete("/item/{item_id}")
def delete_item(request: Request, item_id: int):
    global todo_list
    todo_list = [
        item
        for item in todo_list
        if item["id"] != item_id
    ]
    return templates.TemplateResponse("list.html", {"request": request, "todo_list": todo_list})


@app.get("/item/{item_id}/edit")
def get_edit_item(request: Request, item_id: int):
    global todo_list
    list_item = [
        item
        for item in todo_list
        if item["id"] == item_id
    ]
    if list_item == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse("edit.html", {"request": request, "list_item": list_item[0]})


@app.patch("/item/{item_id}/edit")
def save_edited_item(request: Request, item_id: int, text: Annotated[str, Form()]):
    global todo_list
    list_item = [
        item
        for item in todo_list
        if item["id"] == item_id
    ]
    if list_item == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    list_item[0]["text"] = text
    return templates.TemplateResponse("list_item.html", {"request": request, "list_item": list_item[0]})


@app.patch("/item/{item_id}/done")
def save_edited_item(request: Request, item_id: int):
    global todo_list
    list_item = [
        item
        for item in todo_list
        if item["id"] == item_id
    ]
    if list_item == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    list_item[0]["state"] = "DONE"
    return templates.TemplateResponse("list_item.html", {"request": request, "list_item": list_item[0]})


@app.patch("/item/{item_id}/undo")
def undo_item(request: Request, item_id: int):
    global todo_list
    list_item = [
        item
        for item in todo_list
        if item["id"] == item_id
    ]
    if list_item == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    list_item[0]["state"] = "TODO"
    return templates.TemplateResponse("list_item.html", {"request": request, "list_item": list_item[0]})


@app.post("/item/")
def new_item(text: Annotated[str, Form()], request: Request):
    global todo_list
    max_item_id = max(todo_list, key=lambda item: item["id"])["id"]
    new_item = dict(
        id=max_item_id + 1,
        text=text,
        state="TODO",
    )
    todo_list.append(new_item)
    return templates.TemplateResponse("list_item.html", {"request": request, "list_item": new_item})
