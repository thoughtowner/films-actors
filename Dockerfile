FROM python:3.10.13

WORKDIR /http-server-hw

COPY . .
COPY requirements.txt .

RUN pip install -r requirements.txt