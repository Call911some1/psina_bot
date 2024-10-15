FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей для OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы проекта
COPY . .

# Копируем модель
COPY best.pt /app/runs/detect/train/weights/

# Устанавливаем переменные окружения
ENV API_TOKEN=$API_TOKEN

# Запуск бота
CMD ["python", "bot.py"]
