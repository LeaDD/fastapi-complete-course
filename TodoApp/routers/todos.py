from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Request
from TodoApp.models import Todos
from TodoApp.schemas import TodoRequest
from TodoApp.database import SessionLocal
from starlette import status
from TodoApp.routers.auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="TodoApp/templates")


router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A type alias for dependency injection: Session provided by get_db()
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        access_token = request.cookies.get("access_token") or ""
        user = await get_current_user(access_token)

        if user is None:
            return redirect_to_login()
        
        todos = db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except:
        return redirect_to_login()

### Endpoints
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    return db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
                        user: user_dependency,
                        db: db_dependency, 
                        todo_id: int = Path(gt=0)
                    ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
                        user: user_dependency,
                        db: db_dependency, 
                        todo_request: TodoRequest = Body(...)
                    ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("user_id"))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
                        user: user_dependency,
                        db: db_dependency, 
                        todo_request: TodoRequest = Body(...),
                        todo_id: int = Path(gt=0)                        
                    ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
                        user: user_dependency,
                        db: db_dependency, 
                        todo_id: int = Path(gt=0)
                    ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo_model)
    db.commit()

@router.patch("/todo/{todo_id}/toggle", status_code=status.HTTP_200_OK)
async def toggle_todo_completion(
                        user: user_dependency,
                        db: db_dependency, 
                        todo_id: int = Path(gt=0)
                    ):
    """Toggle the completion status of a todo item"""
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.complete = not todo_model.complete
    db.add(todo_model)
    db.commit()
    return {"id": todo_model.id, "complete": todo_model.complete, "message": "Todo status updated successfully"}

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_todo_stats(user: user_dependency, db: db_dependency):
    """Get statistics about user's todos"""
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    user_todos = db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()
    total_todos = len(user_todos)
    completed_todos = len([todo for todo in user_todos if todo.complete])
    pending_todos = total_todos - completed_todos
    completion_rate = (completed_todos / total_todos * 100) if total_todos > 0 else 0
    
    return {
        "total_todos": total_todos,
        "completed_todos": completed_todos,
        "pending_todos": pending_todos,
        "completion_rate": round(completion_rate, 2)
    }