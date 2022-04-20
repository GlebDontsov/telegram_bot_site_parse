import random
import time

import requests
import telebot
from bs4 import BeautifulSoup as bs

api_url = "https://wax.api.atomicassets.io/atomicassets/v1/collections"

bot = telebot.TeleBot("Token")

time_create_last = 0
users = {}


# создание пользователя
class User:
    def __init__(self, chat_id, first_name, last_name):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name


# команда запуска бота
@bot.message_handler(commands=["start"])
def start(message):
    users["{0}".format(message.chat.id)] = User(message.chat.id, message.from_user.first_name,
                                                message.from_user.last_name)
    first_name = users["{0}".format(message.chat.id)].first_name
    bot.send_message(users["{0}".format(message.chat.id)].chat_id, f"Ok, {first_name}!")
    parse(message)


# команда остановки бота
@bot.message_handler(commands=["stop"])
def stop(message):
    bot.send_message(users["{0}".format(message.chat.id)].chat_id, f"Понял!")
    if "{0}".format(message.chat.id) in users:
        del users["{0}".format(message.chat.id)]


def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # получаем ответ HTTP и создаем объект soup
    soup = bs(requests.get(url).content, "html.parser")
    try:
        proxies = soup.find("textarea").text.split("\n")[3:]
        return proxies[random.randint(1, len(proxies) - 1)]
    except:
        time.sleep(10)
        get_free_proxies()


# отправка сообщений пользователю
def messages(collection_name, url, img, url_website):
    if img != None:
        img_data = requests.get(f"https://resizer.atomichub.io/images/v1/preview?ipfs={img}&size=370",
                                headers=HEADERS).content

        with open("img.webp", "wb") as f:
            f.write(img_data)

        for key in users:
            bot.send_photo(users[key].chat_id, open("img.webp", "rb"))
            bot.send_message(users[key].chat_id, f"Имя коллекции: {collection_name}\n"
                                                 f"Ссылка на коллекцию: {url}\nСсылка на сайт: {url_website}")


# поиск новых коллекций на сайте
def parse(message):
    while True:
        global HEADERS
        proxy = get_free_proxies().split(':')[0]
        HEADERS = {
            "Referer": "https://wax.atomichub.io",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          f"Chrome/{proxy} YaBrowser/22.1.5.810 Yowser/2.5 Safari/537.36",
            "sec-ch-ua-platform": "Windows"
        }

        try:
            res = requests.get(api_url, headers=HEADERS)
        except:
            time.sleep(60)
            parse()

        items = res.json()

        if res.status_code == 200:
            for item in items["data"]:
                global time_create_last
                created_at_time = int(item["created_at_time"][:-3])
                collection_name, img = item["collection_name"], item["img"]

                if time_create_last < created_at_time:
                    time_create_last = created_at_time
                    url = f"https://wax.atomichub.io/explorer/collection/{collection_name}"

                    if "url" in item["data"]:
                        url_website = item["data"]["url"]
                    else:
                        url_website = "Cсылки на сайт нет"

                    messages(collection_name, url, img, url_website)

        else:
            bot.send_message(users["{0}".format(message.chat.id)].chat_id, "Error!")

        time.sleep(5)


bot.polling(none_stop=True)
