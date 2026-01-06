# Версия Питона
FROM python:3.13.5-slim

# Рабочая папка внутри контейнера
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Порт
EXPOSE 8000

# Команда для запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]