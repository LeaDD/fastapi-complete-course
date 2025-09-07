from fastapi import FastAPI
from TodoApp.models import Base
from TodoApp.database import engine
from TodoApp.routers import auth, todos, admin, user

app = FastAPI()

# Create tables (once) on startup. In production you’d use Alembic migrations.
Base.metadata.create_all(bind=engine)

@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)