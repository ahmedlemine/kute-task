from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime


class Task(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    title: str
    created_at: datetime = Field(
        default_factory=datetime.now,
    )
    last_deferred: datetime = Field(
        default_factory=datetime.now,
    )
