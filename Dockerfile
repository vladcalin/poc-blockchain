FROM python:3.6-slim

ADD . /code
RUN pip install -e /code

CMD netnode start --log=debug