import os
from PIL import Image


def resize_and_save(image_path, output_path, size=(256, 256)):
    """
    Изменяет размер изображения и сохраняет его.
    Args:
        image_path (str): Путь к исходному изображению.
        output_path (str): Путь для сохранения измененного изображения.
        size (tuple): Новый размер изображения.
    """
    img = Image.open(image_path)
    # img.thumbnail(size)  # Изменяет размер, сохраняя пропорции
    img.save(output_path)


def process_images(source_dir, output_dir):
    """
    Перебирает изображения в папке и сохраняет их в новую папку с измененным размером.
    Args:
        source_dir (str): Путь к исходной папке.
        output_dir (str): Путь к папке для сохранения.
    """
    os.makedirs(output_dir, exist_ok=True)  # Создает папку, если ее нет
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                output_path = os.path.join(output_dir, file)
                resize_and_save(image_path, output_path)


source_dir = "./images"
output_dir = "./pictures"

process_images(source_dir, output_dir)

print("Обработка завершена!")
