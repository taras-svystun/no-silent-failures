import os

from alembic import context
from sqlalchemy import create_engine

# Tests pass the URL through the Alembic config; the container uses the env var.
url = context.config.get_main_option("sqlalchemy.url") or os.environ["DATABASE_URL"]

with create_engine(url).connect() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
