FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini .
COPY migrations migrations
COPY app app
# exec: uvicorn replaces the shell as PID 1, so it gets Docker's SIGTERM
# and shuts down cleanly instead of being killed after 10 s.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
