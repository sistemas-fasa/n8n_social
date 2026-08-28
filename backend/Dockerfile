FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/alembic.ini /app/alembic.ini
COPY backend/alembic /app/alembic
COPY backend/app /app/app
COPY docker/backend-entrypoint.sh /usr/local/bin/fasa-social-backend-entrypoint.sh
RUN chmod 0755 /usr/local/bin/fasa-social-backend-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/fasa-social-backend-entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
