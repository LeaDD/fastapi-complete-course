from fastapi import FastAPI, Request, status
from TodoApp.models import Base
from TodoApp.database import engine
from TodoApp.routers import auth, todos, admin, user
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import RedirectResponse

app = FastAPI()

# Create tables (once) on startup. In production you’d use Alembic migrations.
Base.metadata.create_all(bind=engine)



app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)

# start with uvicorn TodoApp.main:app --reload --env-file TodoApp/.env
