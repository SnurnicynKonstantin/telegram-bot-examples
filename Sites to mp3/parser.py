import requests
from bs4 import BeautifulSoup
from langdetect import detect
import re


def get_link(message_text):
    # Ищем ссылку в отправленном боту сообщении
    link_arr = re.findall(r'^https?:\/\/?[\w-]{1,32}'
                          r'\.[\w-]{1,32}[^\s@]*$', message_text)
    if len(link_arr) > 0:
        link = link_arr[0]
        return link
    return False


def get_article_text(link):
    try:
        # Получаем ответ от сервера, на который ведет ссылка
        response = requests.get(link)
    except requests.exceptions.ConnectionError:
        return False
    # Инициализируем парсер
    parser = BeautifulSoup(response.content, 'html.parser')
    try:
        # Парсим статью по тегу <article>
        article_text = parser.select_one('article').get_text(separator='. ')
    except AttributeError:
        return False
    return article_text


def get_article_language(article_text):
    try:
        language = detect(article_text)  # Определяем язык статьи
    except TypeError:
        return False
    if language == 'en':
        return ['EN', ['english']]
    if language == 'ru':
        return ['RU', ['russian']]
    return False