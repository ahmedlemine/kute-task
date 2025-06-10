import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from api import TaskAPI, TaskNotFound, InvalidTaskID, MissingTitle, InvalidTitle
from models import Task

test_db_file_name = "tasks_test_db.sqlite3"


@pytest.fixture(scope="module")
def task_api():
    with TemporaryDirectory() as tmp_dir:
        base_dir = Path(tmp_dir)
        db_path = base_dir / test_db_file_name
        sqlite_url = f"sqlite:///{db_path}"
        api = TaskAPI(sqlite_url)
        yield api


def test_empty_db_zero_tasks(task_api):
    assert task_api.count_tasks() == 0


def test_add_multiple_tasks(task_api):
    task_api.add_task(Task(title="Task 1"))
    task_api.add_task(Task(title="Task 2"))
    task_api.add_task(Task(title="Task 3"))
    assert task_api.count_tasks() == 3


def test_add_single_task(task_api):
    title = "test task from pytest"
    t = Task(title=title)
    id = t.id
    new_task_id = task_api.add_task(t)
    assert new_task_id == id


def test_add_task_missing_title(task_api):
    t = Task()
    with pytest.raises(MissingTitle):
        task_api.add_task(t)
        assert isinstance(Task, t)


def test_add_task_invalid_title(task_api):
    t = Task(title=123)
    with pytest.raises(InvalidTitle):
        task_api.add_task(t)
        assert isinstance(Task, t)


def test_list_tasks(task_api):
    t = Task(title="Task 1")
    new_task_id = task_api.add_task(t)
    assert task_api.list_tasks()[-1].id == new_task_id


def test_get_task(task_api):
    t = Task(title="test task")
    id = task_api.add_task(t)
    new_task_id = str(id)
    retrieved_task_id = task_api.get_task(new_task_id).id
    assert str(retrieved_task_id) == new_task_id


def test_get_non_existent_task(task_api):
    id = str(uuid4())
    with pytest.raises(TaskNotFound):
        assert task_api.get_task(id) == id


