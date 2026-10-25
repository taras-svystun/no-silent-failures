from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import Task, engine, get_session

app = FastAPI(title="no-silent-failures")
SessionDep = Annotated[Session, Depends(get_session)]


class TaskIn(BaseModel):
    title: str
    done: bool = False


class TaskOut(TaskIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


def get_task_or_404(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(body: TaskIn, session: SessionDep):
    task = Task(**body.model_dump())
    session.add(task)
    session.commit()
    return task


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(session: SessionDep):
    return session.scalars(select(Task).order_by(Task.id)).all()


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, session: SessionDep):
    return get_task_or_404(session, task_id)


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, body: TaskIn, session: SessionDep):
    task = get_task_or_404(session, task_id)
    task.title, task.done = body.title, body.done
    session.commit()
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: SessionDep):
    session.delete(get_task_or_404(session, task_id))
    session.commit()


@app.get("/health")
def health():
    # A health check that does not touch the DB would say "ok" while every
    # real request fails: a silent failure.
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "db down"})
    return {"status": "ok"}
