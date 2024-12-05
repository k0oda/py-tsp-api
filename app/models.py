from pydantic import HttpUrl
from sqlmodel import Field, Relationship, SQLModel


class RecordBase(SQLModel):
    pass


class Record(RecordBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dialog: list["DialogItem"] | None = Relationship(
        back_populates="record",
        sa_relationship_kwargs={
            "cascade": "all,delete-orphan",
        },
    )
    audio_path: str = Field(default=None)


class RecordResultDuration(SQLModel):
    receiver: float
    transmitter: float


class RecordPublic(RecordBase):
    dialog: list["DialogItemPublic"]
    result_duration: RecordResultDuration


class RecordRequest(RecordBase):
    audio_source: str | HttpUrl


class DialogItemBase(SQLModel):
    source: str = Field(default=None)
    text: str = Field(default=None)
    duration: float = Field(default=None)
    raised_voice: bool = Field(default=None)
    gender: str = Field(default=None)


class DialogItem(DialogItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    record_id: int = Field(default=None, foreign_key="record.id")
    record: Record | None = Relationship(back_populates="dialog")


class DialogItemPublic(DialogItemBase):
    pass
