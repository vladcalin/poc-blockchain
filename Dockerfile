FROM python:3.6-slim

ADD . /code
RUN pip install -e /code[node]

CMD netnode start --log=debug