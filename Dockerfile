FROM python:3.9.6

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app

ADD . /app

RUN apt-get update

RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app
