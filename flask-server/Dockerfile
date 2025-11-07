FROM python:3.11-slim

WORKDIR /flask-server

COPY requirements.txt

run pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]