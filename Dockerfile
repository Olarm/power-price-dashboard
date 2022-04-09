FROM python:3.9-slim-buster

# set working directory in container
RUN mkdir /app
WORKDIR /app

# Copy and install packages
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Copy app folder to app folder in container
COPY ./src/ /app/
COPY secrets.py /app/

# Changing to non-root user
RUN useradd -m appUser
USER appUser

# Run locally
CMD gunicorn --bind 0.0.0.0:8050 app:server
