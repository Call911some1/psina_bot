FROM python:3.10-slim

WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Копируем модель из локальной машины в контейнер
COPY best.pt /app/runs/detect/train/weights/

# Не указываем токен прямо в Dockerfile
ENV API_TOKEN=$API_TOKEN

# Запуск бота
CMD ["python", "bot.py"]
