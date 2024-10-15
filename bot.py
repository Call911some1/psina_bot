import os
from aiogram import Bot, Dispatcher, types
from aiogram import Router
from aiogram.types import InputFile
import asyncio
from ultralytics import YOLO
import logging

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токен Telegram-бота из переменной окружения
API_TOKEN = os.getenv('API_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем роутер
router = Router()

# Загружаем обученную модель YOLOv8
model = YOLO('/app/runs/detect/train/weights/best.pt')

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
@router.message(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне изображение, и я выполню детекцию объектов с помощью YOLOv8!")

# Обработчик изображений
@router.message(content_types=["photo"])
async def handle_photo(message: types.Message):
    photo = message.photo[-1]  # выбираем изображение с наибольшим разрешением
    file_info = await bot.get_file(photo.file_id)
    image_path = f"/app/downloads/{photo.file_id}.jpg"
    await bot.download_file(file_info.file_path, image_path)

    # Выполняем детекцию объектов
    detected_image_path = await detect_objects(image_path)

    if detected_image_path:
        with open(detected_image_path, 'rb') as photo_file:
            await message.answer_photo(photo_file)
    else:
        await message.reply("Не удалось обнаружить объекты на изображении.")

# Запуск бота
async def main():
    # Убедись, что директория 'downloads' существует
    if not os.path.exists('/app/downloads'):
        os.makedirs('/app/downloads')

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
