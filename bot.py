import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor
from ultralytics import YOLO
import logging

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токен Telegram-бота из переменной окружения
API_TOKEN = os.getenv('API_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Загружаем обученную модель YOLOv8
model = YOLO('/app/runs/detect/train/weights/best.pt')  # Путь внутри Docker-контейнера

# Функция для выполнения инференса и детекции объектов
async def detect_objects(image_path):
    results = model.predict(source=image_path, save=True)
    output_dir = '/app/runs/detect/predict/'  # путь, куда сохраняются результаты в контейнере
    result_images = os.listdir(output_dir)
    if result_images:
        return os.path.join(output_dir, result_images[-1])  # возвращаем последний результат
    else:
        return None

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне изображение, и я выполню детекцию объектов с помощью YOLOv8!")

# Обработчик изображений
@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    # Скачиваем изображение
    photo = message.photo[-1]  # выбираем изображение с наибольшим разрешением
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path

    # Скачиваем изображение в локальную директорию
    image_path = f"/app/downloads/{photo.file_id}.jpg"  # Путь для скачивания в контейнере
    await photo.download(destination_file=image_path)

    # Выполняем детекцию объектов
    detected_image_path = await detect_objects(image_path)

    # Отправляем результат обратно пользователю
    if detected_image_path:
        with open(detected_image_path, 'rb') as photo_file:
            await bot.send_photo(message.chat.id, photo=photo_file)
    else:
        await message.reply("Не удалось обнаружить объекты на изображении.")

# Запуск бота
if __name__ == '__main__':
    # Убедись, что директория 'downloads' существует
    if not os.path.exists('/app/downloads'):
        os.makedirs('/app/downloads')

    executor.start_polling(dp, skip_updates=True)