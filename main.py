import os
from dotenv import load_dotenv
import requests
from dadata import Dadata
import telebot

load_dotenv()

telegramToken = os.getenv('TELEGRAM_BOT_TOKEN')
yandex_access_key = os.getenv('YANDEX_ACCESS_KEY')
dadataToken = os.getenv('DADATA_TOKEN')
dadataSecret = os.getenv('DADATA_SECRET')

if not telegramToken:
    print("TELEGRAM_BOT_TOKEN не найден")
if not yandex_access_key:
    print("YANDEX_ACCESS_KEY не найден")
if not dadataToken or not dadataSecret:
    print("DADATA токены не найдены")


bot = telebot.TeleBot(telegramToken)

#yandex
headers = {
    'X-Yandex-Weather-Key': yandex_access_key
}

#dadata
dadata = Dadata(dadataToken, dadataSecret)


def getWeather(lat, lon):
    response = requests.get(f'https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}', headers=headers)
    return response.json()

def getCordinates(city):
    result = dadata.clean("address", city)
    return result

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Введите город России")


@bot.message_handler(func=lambda message: True)
def handle_name(message):
    name = message.text
    getCords = getCordinates(name)

    if getCords == None or getCords['geo_lat'] == None or getCords['geo_lon'] == None:
        bot.send_message(message.chat.id, 'Нужен город России')
        return

    lat = getCords['geo_lat']
    lon = getCords['geo_lon']

    weather = getWeather(lat, lon)

    if weather is None:
        bot.send_message(message.chat.id, 'Ошибка при запросе погоды')
        return

    bot.send_message(message.chat.id,
                 f"Погода в городе {name}: {weather['fact']['temp']}°C, влажность: {weather['fact']['humidity']}%, давление: {weather['fact']['pressure_pa']} мм.рт.ст/{weather['fact']['pressure_pa']} Па")


if __name__ == '__main__':
    bot.infinity_polling()

