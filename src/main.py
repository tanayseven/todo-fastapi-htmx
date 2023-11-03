from typing import Annotated

from fastapi import FastAPI, Request, Form
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


class ItemRequest(BaseModel):
    text: str


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
