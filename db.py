from sqlmodel import SQLModel, create_engine
from sqlalchemy import inspect
from pathlib import Path
from platformdirs import user_data_path

appname = "Kute Task"
appauthor = "Kute Apps"
base_dir = Path(user_data_path(appname, appauthor))

sqlite_file_name = ".tasks_db.sqlite3"
db_path = base_dir / sqlite_file_name
sqlite_url = f"sqlite:///{db_path}"

def get_engine(db_url: str = sqlite_url):
    """Checks if database & table(s) exist, if not creates them"""
    engine = create_engine(db_url, echo=True)
    insp = inspect(engine)
    db_table_exists = insp.has_table("task")

    if not db_table_exists:
        SQLModel.metadata.create_all(engine)
        print(f"Created a new database at {sqlite_file_name}")
    return engine
