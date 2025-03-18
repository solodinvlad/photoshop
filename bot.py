import telebot
from PIL import Image, ImageFilter, ImageChops
import os

bot = telebot.TeleBot('7431905855:AAF7IwC-5FfKlWNRFXDErU0oNXfYxTViZxw')
user_states = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.reply_to(message,
                 "Привет! Я бот для обработки фотографий. Отправь мне фото, и я помогу его обработать.",
                 reply_markup=markup)


# Получение фотографии от пользователя
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Получаем ID самой большой версии фото из массива (последний элемент)
    file_id = message.photo[-1].file_id
    # Запрашиваем информацию о файле через Telegram API
    file_info = bot.get_file(file_id)
    # Скачиваем файл как байтовый поток
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем фото локально с уникальным именем, используя ID чата
    photo_path = f"photo_{message.chat.id}.jpg"
    with open(photo_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Сохраняем путь к файлу в словаре состояний
    user_states[message.chat.id] = {'photo_path': photo_path}

    # Создаем меню обработки
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Черно-белое")
    btn2 = telebot.types.KeyboardButton("Размытие")
    btn3 = telebot.types.KeyboardButton("Повернуть")
    btn4 = telebot.types.KeyboardButton("Сделать квадратным")
    btn5 = telebot.types.KeyboardButton("Сократить цвета")
    btn6 = telebot.types.KeyboardButton("Негатив")
    btn7 = telebot.types.KeyboardButton("Новое фото")
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    markup.add(btn7)
    bot.reply_to(message, "Выберите действие с фото:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Негатив')
def negative(message):
    if message.chat.id not in user_states:
        bot.reply_to(message, "Сначала отправьте фото!")
        return
    photo_path = user_states[message.chat.id]['photo_path']
    img = ImageChops.invert(Image.open(photo_path))
    output_path = f"negative_{message.chat.id}.jpg"
    img.save(output_path)
    with open(output_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(output_path)


@bot.message_handler(func=lambda message: message.text == "Черно-белое")
def make_bw(message):
    if message.chat.id not in user_states:
        bot.reply_to(message, "Сначала отправьте фото!")
        return
    photo_path = user_states[message.chat.id]['photo_path']
    img = Image.open(photo_path).convert('L')
    output_path = f"bw_{message.chat.id}.jpg"
    img.save(output_path)
    with open(output_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(output_path)


@bot.message_handler(func=lambda message: message.text == "Размытие")
def blur(message):
    if message.chat.id not in user_states:
        bot.reply_to(message, "Сначала отправьте фото!")
        return
    photo_path = user_states[message.chat.id]['photo_path']
    img = Image.open(photo_path).filter(ImageFilter.GaussianBlur(radius=15))
    output_path = f"blur_{message.chat.id}.jpg"
    img.save(output_path)
    with open(output_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(output_path)


@bot.message_handler(func=lambda message: message.text == "Повернуть")
def rotate(message):
    if message.chat.id not in user_states:
        bot.reply_to(message, "Сначала отправьте фото!")
        return
    photo_path = user_states[message.chat.id]['photo_path']
    img = Image.open(photo_path).rotate(270)
    output_path = f"rotate_{message.chat.id}.jpg"
    img.save(output_path)
    with open(output_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(output_path)


@bot.message_handler(func=lambda message: message.text == "Сделать квадратным")
def resize(message):
    if message.chat.id not in user_states:
        bot.reply_to(message, "Сначала отправьте фото!")
        return
    photo_path = user_states[message.chat.id]['photo_path']
    img = Image.open(photo_path)
    img = img.resize((800, 800))
    output_path = f"resize_{message.chat.id}.jpg"
    img.save(output_path)
    with open(output_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(output_path)


@bot.message_handler(func=lambda message: message.text == "Сократить цвета")
def quantize(message):
    if message.chat.id not in user_states:
        bot.reply_to(message, "Сначала отправьте фото!")
        return
    photo_path = user_states[message.chat.id]['photo_path']
    img = Image.open(photo_path).quantize(colors=16)
    img = img.convert('RGB')
    output_path = f"quant_{message.chat.id}.jpg"
    img.save(output_path)
    with open(output_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(output_path)


@bot.message_handler(func=lambda message: message.text == "Новое фото")
def new_photo(message):
    bot.reply_to(message, 'Отправьте новое фото')


if __name__ == "__main__":
    bot.polling(none_stop=True)