FROM python:3.10-slim

WORKDIR /backend

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8034
CMD ["python", "./server/app.py"]