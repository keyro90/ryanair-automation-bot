FROM ubuntu:20.04

ENV PYTHONUNBUFFERED 1

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /code

RUN mkdir /driver

WORKDIR /code

COPY requirements.txt /code/

RUN apt-get update

RUN apt-get upgrade -y

RUN apt-get install python3.8 python3-pip python-is-python3 firefox -y

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /code/

CMD ["bash" , "-c", "./start.sh"]
