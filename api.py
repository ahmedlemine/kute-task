from sqlmodel import Session, select, func, delete
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from uuid import UUID

from db import get_engine
from models import Task


class TaskException(Exception):
    pass


class TaskNotFound(TaskException):
    pass


class InvalidTaskID(TaskException):
    pass


class MissingTitle(TaskException):
    pass


class InvalidTitle(TaskException):
    pass


class TaskAPI:
    """API for the Single Task app"""

    def __init__(self, db_url):
        self.db_url = db_url
        self._engine = get_engine(db_url)

    def add_task(self, task: Task) -> UUID:
        """Add a task and return the id of the task."""
        if not task.title:
            raise MissingTitle("a task must have a title.")

        if not isinstance(task.title, str):
            raise InvalidTitle("task title must be a string.")
        with Session(self._engine) as session:
            task_id = task.id
            session.add(task)
            session.commit()
            return task_id

    def list_all_tasks(self) -> list[Task]:
        """List all tasks in DB."""
        with Session(self._engine) as session:
            statement = select(Task)
            results = session.exec(statement)
            tasks = results.all()
            return tasks

    def list_incomplet_by_last_deferred(self) -> list[Task]:
        """List only incomplete tasks orderd by last_deferred first."""
        with Session(self._engine) as session:
            statement = (
                select(Task)
                .where(Task.is_completed == False)
                .order_by(Task.last_deferred.asc())
            )
            results = session.exec(statement)
            tasks = results.all()
            return tasks

    def list_completed_tasks(self) -> list[Task]:
        """List only completed tasks."""
        with Session(self._engine) as session:
            statement = select(Task).where(Task.is_completed == True)
            results = session.exec(statement)
            tasks = results.all()
            return tasks

    def list_incomplete_tasks(self) -> list[Task]:
        """List only incompleted tasks."""
        with Session(self._engine) as session:
            statement = select(Task).where(Task.is_completed == False)
            results = session.exec(statement)
            tasks = results.all()
            return tasks

    def get_task(self, id: UUID) -> Task:
        """Retrieve a single task by id."""
        if not isinstance(id, str):
            raise InvalidTaskID("Task id must be a string.")
        with Session(self._engine) as session:
            statement = select(Task).where(Task.id == UUID(id))
            try:
                task = session.exec(statement).one()
                return task
            except NoResultFound as e:
                raise TaskNotFound(f"[Error] No results found for the given id: {e}")

    def delete_task(self, id: UUID) -> None:
        """Delete a single task by id."""
        task = self.get_task(id)
        if task is not None:
            with Session(self._engine) as session:
                try:
                    session.delete(task)
                    session.commit()
                except NoResultFound as e:
                    raise TaskNotFound(
                        f"[Error] No results found for the given id: {e}"
                    )
        else:
            raise TaskNotFound(
                "[Error] can't defer task. No results found for the given id"
            )

    def defer_task(self, id: UUID) -> None:
        """Defer a task by id."""
        task = self.get_task(id)
        if task is not None:
            with Session(self._engine) as session:
                task.last_deferred = datetime.now()
                session.add(task)
                session.commit()
                session.refresh(task)
        else:
            raise TaskNotFound(
                "[Error] can't defer task. No results found for the given id"
            )

    def get_next_task(self) -> Task:
        """Retrieve next task in the queue."""
        with Session(self._engine) as session:
            statement = (
                select(Task)
                .where(Task.is_completed == False)
                .order_by(Task.last_deferred.asc())
            )
            results = session.exec(statement)
            next_task = results.first()
            return next_task

    def toggle_complete(self, id: UUID) -> Task:
        """Toggle a task's is_completed"""
        task = self.get_task(id)
        if task is not None:
            with Session(self._engine) as session:
                task.is_completed = not task.is_completed
                session.add(task)
                session.commit()
                session.refresh(task)
                return task
        else:
            raise TaskNotFound(
                "[Error] can't complete task. No results found for the given id"
            )

    def count_tasks(self) -> int:
        """Return the count of all tasks in the DB."""
        with Session(self._engine) as session:
            statement = select(func.count()).select_from(Task)
            results = session.exec(statement)
            task_count = results.one()
            return task_count

    def delete_all_tasks(self) -> None:
        """Delete all tasks from the DB."""
        with Session(self._engine) as session:
            statement = delete(Task)
            session.exec(statement)
            session.commit()
