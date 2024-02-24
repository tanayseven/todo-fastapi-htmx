from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from sqladmin import Admin
from src.database import engine
from src.ext import templates
from src.todo_list.admin import ListItemView
# from src.user.admin import UserView
from src.todo_list.routes import router as todo_list_router

app = FastAPI()
admin = Admin(app, engine, title="Admin")

app.mount("/static", StaticFiles(directory="static"), name="static")

# All the routes
app.include_router(todo_list_router)

# All the admin views
# admin.add_view(UserView)
admin.add_view(ListItemView)


@app.middleware("http")
async def exception_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.debug(e)
        return templates.TemplateResponse(
            "dialogs/server_error.html", {"request": request}, status_code=500
        )
