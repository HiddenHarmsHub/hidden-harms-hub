FROM python:3.12-slim-bookworm

RUN apt-get update && \
    apt-get upgrade -y

COPY pyproject.toml /pyproject.toml

# Install requirements from the project
RUN pip install --upgrade pip && \
    pip install .["lint","test"]

RUN rm /pyproject.toml
