FROM python:3.8
ENV PYTHONUNBUFFERED 1

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements
COPY ./requirements /usr/src/app/requirements

# install requirements
RUN pip install -r requirements/local.txt

# add app
COPY . /usr/src/app

# add user
RUN adduser --disabled-password --gecos '' app_user

EXPOSE 8000
