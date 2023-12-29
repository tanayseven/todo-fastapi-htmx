from sqladmin import ModelView
from src.todo_list.schema import ListItem
from src.user.schema import User


class UserView(ModelView, model=User):
    __tablename__ = "user"

    column_list = [User.id, User.email, User.is_active, User.is_superuser, User.is_verified]
