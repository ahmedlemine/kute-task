from sqlmodel import SQLModel, create_engine
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError as sqlalchemy_op_err
from sqlite3 import OperationalError as sqlite_op_err
from pathlib import Path
from platformdirs import user_data_path


class DBException(Exception):
    pass


class DBConnectionFaild(DBException):
    pass


appname = "kute-task"
appauthor = "kute-apps"
base_dir = Path(user_data_path(appname, appauthor))

sqlite_file_name = ".tasks_db.sqlite3"
db_path = base_dir / sqlite_file_name
sqlite_url = f"sqlite:///{db_path}"


def get_engine(db_url: str = sqlite_url):
    """Creates DB base_dir, create the SQLModel engine
    then checks if database & table(s) exist, if not creates them
    """
    base_dir.mkdir(exist_ok=True)
    try:
        engine = create_engine(db_url, echo=False)
        insp = inspect(engine)
        db_table_exists = insp.has_table("task")
    except sqlalchemy_op_err as e:
        raise DBConnectionFaild(f"[Error] Faild to create or connect to the DB: {e}")
    except sqlite_op_err as e:
        raise DBConnectionFaild(f"Faild to create or connect to the DB: {e}")

    if not db_table_exists:
        SQLModel.metadata.create_all(engine)
    return engine
