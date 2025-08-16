from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from ..core import schemas
from ..core.db import get_db
from ..core.models import Task, User
from ..core.security import get_current_user
from ..core.cache import cache_get, cache_set, cache_delete_pattern
import json

router = APIRouter()

def _task_key(user_id: int, task_id: int) -> str:
    return f"task:{user_id}:{task_id}"

def _list_key(user_id: int, skip: int, limit: int, status: Optional[str]) -> str:
    suffix = f":{status}" if status else ""
    return f"tasks:{user_id}:{skip}:{limit}{suffix}"

@router.post("/", response_model=schemas.TaskOut, status_code=201)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = Task(**payload.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    # invalidate caches
    cache_delete_pattern(f"tasks:{current_user.id}:*")
    return task

@router.get("/", response_model=List[schemas.TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(todo|in_progress|done)$")
):
    key = _list_key(current_user.id, skip, limit, status)
    cached = cache_get(key)
    if cached:
        return json.loads(cached)

    q = db.query(Task).filter(Task.owner_id == current_user.id)
    if status:
        q = q.filter(Task.status == status)
    tasks = q.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    tasks_data = [schemas.TaskOut.model_validate(t).model_dump() for t in tasks]
    cache_set(key, tasks_data, ttl=60)  # cache for 60s
    return tasks_data

@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    key = _task_key(current_user.id, task_id)
    cached = cache_get(key)
    if cached:
        return json.loads(cached)

    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    data = schemas.TaskOut.model_validate(task).model_dump()
    cache_set(key, data, ttl=60)
    return data

@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(task, k, v)
    db.add(task)
    db.commit()
    db.refresh(task)

    # Invalidate caches
    cache_delete_pattern(_task_key(current_user.id, task_id))
    cache_delete_pattern(f"tasks:{current_user.id}:*")
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    # Invalidate caches
    cache_delete_pattern(_task_key(current_user.id, task_id))
    cache_delete_pattern(f"tasks:{current_user.id}:*")
    return None
