FROM arm32v6/python:3.8-alpine

LABEL maintainer="Lukas Voegtle <voegtlel@tf.uni-freiburg.de>"

RUN pip install --no-cache-dir uvicorn gunicorn

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]

RUN pip install --no-cache-dir fastapi

# Local installation

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install --no-root

COPY ./device_server /app/device_server

ENV MODULE_NAME=device_server.api
ENV VARIABLE_NAME=app
