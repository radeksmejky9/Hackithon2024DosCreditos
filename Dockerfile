FROM python:3.10-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app/__init__.py:server
CMD ["flask", "run", "--host=0.0.0.0"]
