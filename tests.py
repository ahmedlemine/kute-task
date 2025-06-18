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


def test_add_task_invalid_title(task_api):
    t = Task(title=123)
    with pytest.raises(InvalidTitle):
        task_api.add_task(t)


def test_list_all_tasks(task_api):
    t = Task(title="Task 1")
    new_task_id = task_api.add_task(t)
    assert task_api.list_all_tasks()[-1].id == new_task_id


def test_list_incomplete_tasks(task_api):
    """list_incomplete_tasks() should return all tasks that have is_completed=False
    and not any tasks that has is_completed=True
    """
    t1 = Task(title="incomplete task", is_completed=False)
    t2 = Task(title="completed task", is_completed=True)
    incmplt_task_id = task_api.add_task(t1)
    cmplt_task_id = task_api.add_task(t2)
    tasks = task_api.list_incomplete_tasks()
    incmplt_tasks = list(map(lambda t: t.id if not t.is_completed else None, tasks))
    assert incmplt_task_id in incmplt_tasks and cmplt_task_id not in incmplt_tasks


def test_list_completed_tasks(task_api):
    """list_completed_tasks() should return all tasks that have is_completed=True
    and not any tasks that has is_completed=False
    """
    t1 = Task(title="completed task", is_completed=True)
    t2 = Task(title="incomplete task", is_completed=False)
    cmplt_task_id = task_api.add_task(t1)
    incmplt_task_id = task_api.add_task(t2)
    tasks = task_api.list_completed_tasks()
    cmplt_tasks = list(map(lambda t: t.id if t.is_completed else None, tasks))
    assert cmplt_task_id in cmplt_tasks and incmplt_task_id not in cmplt_tasks


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

def test_update_task_title(task_api):
    t = Task(title="Title to be updated")
    old_title = t.title
    old_task_id = task_api.add_task(t)
    updated_task = task_api.update_task_title(str(old_task_id), "new title")
    assert updated_task.title != old_title

def test_update_task_missing_title(task_api):
    t = Task(title="Title to be updated")
    id = task_api.add_task(t)
    with pytest.raises(MissingTitle):
        task_api.update_task_title(str(id), None)


def test_delete_a_single_task(task_api):
    """Deleting a task and then attempting to
    retrieve it shuold raise a TaskNotFound exception. If not,
    the test fails.
    """
    t = Task(title="test task to delete")
    id = str(t.id)
    task_api.add_task(t)
    task_api.delete_task(id)
    with pytest.raises(TaskNotFound):
        assert task_api.get_task(id) is None


def test_delete_a_single_task_from_many(task_api):
    """Testing delete a single task where there is more not deleted
    by recording initial DB task counts,
    adding 2 tasks, deleting one of them, then comparing if the count has
    increased by only 1 (1 represnting the task added but not deleted.)
    """
    init_count = task_api.count_tasks()
    t1 = Task(title="test task to delete")
    t2 = Task(title="test task to sty")
    added_task1_id = task_api.add_task(t1)
    task_api.add_task(t2)
    task_api.delete_task(str(added_task1_id))
    assert task_api.count_tasks() == init_count + 1


def test_delete_non_existent_task(task_api):
    id = str(uuid4())
    with pytest.raises(TaskNotFound):
        assert task_api.delete_task(id) is None


def test_delete_task_with_invalid_id(task_api):
    """delete_task() takes one argument: a str of the task id
    to delete. Here, we're giving it an int.
    """
    id = 1234
    with pytest.raises(InvalidTaskID):
        assert task_api.delete_task(id) is None


def test_delete_all_tasks(task_api):
    task_api.delete_all_tasks()
    assert task_api.count_tasks() == 0


def test_defer_task(task_api):
    """defer_task() should update the last_deferred field of
    a task to the current tiemstamp.
    Which should push that task to the bottom of task list
    when retrieved by last_deferred first.
    This funciont tests if defferring a task pushes it to the -1 index
    """
    t = Task(title="task to be deferred")
    added_task_id = task_api.add_task(t)
    task_api.defer_task(str(added_task_id))
    assert task_api.list_incomplet_by_last_deferred()[-1].id == added_task_id


def test_defer_task_with_invalid_id(task_api):
    """defer_tak() takes one argument: a str of the task id
    to defere. Here, we're giving it an int.
    """
    id = 1234
    with pytest.raises(InvalidTaskID):
        assert task_api.defer_task(id) is None


def test_get_next_task(task_api):
    """Get_next_task() should return the task at [0] index
    of the task list if ordered by created_at
    """
    t1 = Task(title="Task 1")
    t2 = Task(title="Task 2")
    task_api.add_task(t1)
    task_api.add_task(t2)
    next_task = task_api.get_next_task()
    first_task_in_task_list = task_api.list_all_tasks()[0]
    assert next_task.id == first_task_in_task_list.id


def test_get_next_task_returns_a_task(task_api):
    """Tests if get_next_task() actually returns a Task"""
    t1 = Task(title="Task 1")
    t2 = Task(title="Task2")
    task_api.add_task(t1)
    task_api.add_task(t2)
    next_task = task_api.get_next_task()
    assert isinstance(next_task, Task)


def test_get_task_with_invalid_id(task_api):
    """get_task() takes one argument: a str of the task id to get.
    Here, we're giving it an int.
    """
    id = 1234
    with pytest.raises(InvalidTaskID):
        assert task_api.get_task(id).id == id


def test_list_incomplet_by_last_deferred(task_api):
    """Add a couple of tasks then defer a specfic one, which should
    push it to the bottom of the tasks if listed by last_deferred first
    (or most recent deferred last) then check if it indeed gets pushed to theme
    -1 index.
    """
    t1 = Task(title="Latest task")
    t2 = Task(title="Task to be deferred")
    deferred_task_id = t2.id
    task_api.add_task(t1)
    task_api.add_task(t2)
    task_api.defer_task(str(deferred_task_id))
    assert task_api.list_incomplet_by_last_deferred()[-1].id == deferred_task_id


def test_toggle_task_from_false(task_api):
    """Test toggling a task.is_completed from False to True"""
    t = Task(title="Task to toggle", is_completed=False)
    new_task_id = str(task_api.add_task(t))
    completed_task = task_api.toggle_complete(new_task_id)
    assert completed_task.is_completed is True


def test_toggle_task_from_true(task_api):
    """Test toggling a task.is_completed from True to False"""
    t = Task(title="Task to toggle", is_completed=True)
    new_task_id = str(task_api.add_task(t))
    completed_task = task_api.toggle_complete(new_task_id)
    assert completed_task.is_completed is False

def test_toggle_non_existent_task(task_api):
    """Test toggling a non-existent task"""
    id = str(uuid4())
    with pytest.raises(TaskNotFound):
        assert task_api.toggle_complete(id).id == id