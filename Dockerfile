# Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Устанавливаем необходимые системные зависимости для OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы проекта
COPY . .

# Копируем модель из локальной машины в контейнер
COPY best.pt /app/runs/detect/train/weights/

# Не указываем токен прямо в Dockerfile
ENV API_TOKEN=$API_TOKEN

# Запуск бота
CMD ["python", "bot.py"]