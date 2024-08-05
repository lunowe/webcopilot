FROM python:3.11

RUN pip install Flask flask_cors flask_socketio langchain gunicorn langchain_community langchain_openai langchain_core langchain_text_splitters beautifulsoup4

COPY src/ app/
WORKDIR /app

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 backend:app