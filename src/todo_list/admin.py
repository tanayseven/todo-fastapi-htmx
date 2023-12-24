from sqladmin import ModelView
from src.todo_list.schema import ListItem


class ListItemView(ModelView, model=ListItem):
    column_list = [ListItem.id, ListItem.text, ListItem.state]
