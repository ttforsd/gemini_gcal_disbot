FROM python:3.13-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install libmagic1 -y

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "disbot.py"]