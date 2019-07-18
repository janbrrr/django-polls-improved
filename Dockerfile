# pull official base image
FROM python:3.7-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 (required for postgres)
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements/ /usr/src/app/requirements/
COPY ./requirements-prod.txt /usr/src/app/requirements-prod.txt
RUN pip install -r requirements-prod.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY ./mysite/ /usr/src/app/mysite/
COPY ./polls/ /usr/src/app/polls/
COPY ./manage.py /usr/src/app/manage.py

# build docs (build directory is excluded via .dockerignore)
COPY ./docs/ /usr/src/app/docs/
RUN apk add make
RUN cd docs && make html

# remove dev settings to default to production
RUN rm /usr/src/app/mysite/settings/development.py

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
