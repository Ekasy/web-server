FROM python:3.8-slim

WORKDIR /app

COPY . /app

EXPOSE 8080

CMD ["python3", "./main.py"]
