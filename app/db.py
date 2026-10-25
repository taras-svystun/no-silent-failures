import os

from sqlalchemy import Boolean, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# pool_pre_ping: test a pooled connection before use, so a DB restart
# does not hand the next request a dead connection.
# connect_timeout: when the DB is gone, fail in 2 s instead of hanging.
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    connect_args={"connect_timeout": 2},
)


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    done: Mapped[bool] = mapped_column(Boolean, default=False)


def get_session():
    with Session(engine) as session:
        yield session
