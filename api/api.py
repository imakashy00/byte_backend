from fastapi import FastAPI,APIRouter,Depends,HTTPException,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from database.database import Tasks, get_db
from schema.schema import Task, TasksDatabase

# Initializing the FastAPI task router
task_router = APIRouter()

# Route to create a task
@task_router.post("/tasks",dependencies = [Depends(get_current_user)])
async def tasks(task:Task,db:Session = Depends(get_db)):
    '''
    Args:
    task: Task schema
    db: database session

    Returns:
    JSONResponse -> status code and message
    '''
    new_task = Tasks(
        title=task.title.strip().capitalize(), 
        description=task.description.strip().capitalize(), 
        status=task.status
        )
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": status.HTTP_201_CREATED,
                "message": f"Task '{new_task.title}' created successfully"
            }
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


# Route to get all tasks
@task_router.get("/tasks",response_model=list[TasksDatabase],dependencies = [Depends(get_current_user)])
async def tasks(db:Session = Depends(get_db))-> list[TasksDatabase]:
    '''
    Args:
    db: database session
    
    Returns:
    list of tasks from database if available else raise error 404 -> Tasks not found
    '''
    try:
        tasks = db.query(Tasks).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found")
    

# Route to get a single task
@task_router.get("/tasks/{task_id}",dependencies = [Depends(get_current_user)])
async def tasks(task_id:int,db:Session = Depends(get_db)):
    '''
    Args:
    task_id: task id
    db: database session

    Returns:
    task from database if available else raise error 404 -> Task not found
    '''
    try:
        task = db.query(Tasks).filter(Tasks.id == task_id).first()
        if task is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": f"Task with id {task_id} not found"
                })
        return TasksDatabase(**task.__dict__)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")
    

# Route to update a task
@task_router.put("/tasks/{task_id}",dependencies = [Depends(get_current_user)])
async def tasks(task_id:int,task:Task,db:Session = Depends(get_db))-> str:
    '''
    Args:
    task_id: task id
    task: Task schema
    db: database session

    Returns:
    JSONResponse -> status code and message 
    '''
    try:
        update_task = db.query(Tasks).filter(Tasks.id == task_id).first()
        update_task.title = task.title
        update_task.description = task.description
        update_task.status = task.status
        db.commit()
        db.refresh(update_task)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": status.HTTP_200_OK,
                "message": f"Task '{update_task.title}' updated successfully"
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    

# Route to delete a task
@task_router.delete("/tasks/{task_id}",dependencies = [Depends(get_current_user)])
async def tasks(task_id:int,db:Session = Depends(get_db))-> str:
    '''
    Args:
    task_id: task id
    db: database session

    Returns:
    JSONResponse -> status code and message
    '''
    try:
        delete_task =  db.query(Tasks).filter(Tasks.id == task_id).first()
        db.delete(delete_task)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": status.HTTP_200_OK,
                "message": f"Task '{delete_task.title}' deleted successfully"
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not deleted")