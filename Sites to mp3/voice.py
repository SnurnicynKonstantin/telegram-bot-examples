import pyttsx3
from pydub import AudioSegment
import re
import os


def engine_settings(engine, article_language):
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 185)  # Выставляем скорость чтения голоса

    # for voice in voices:
    #     print('=======')
    #     print('Имя: %s' % voice.name)
    #     print('ID: %s' % voice.id)
    #     print('Язык(и): %s' % voice.languages)
    #     print('Пол: %s' % voice.gender)
    #     print('Возраст: %s' % voice.age)

    for voice in voices:
        if voice.name == 'english' and \
                voice.gender == 'male':
            print('voice ' + str(voice.id))
            return engine.setProperty('voice', voice.id)  # Выбираем подходящий голос


def get_mp3_file(file_name, article_text, article_language):
    print('Hello World 2')
    engine = pyttsx3.init()

    engine_settings(engine, article_language)  # Применение настроек голоса
    print('File name = ' + file_name)
    engine.save_to_file("text", file_name)  # Сохранение текста статьи в аудиофайл
    engine.runAndWait()
    print('Hello World 3')
    convert_file_to_mp3(file_name)  # Конвертация в mp3 формат


def convert_file_to_mp3(file_name):
    converter = AudioSegment
    print('Hello World 4')
    converter_file = converter.from_file(file_name)
    print('Hello World 5')
    converter_file.export(file_name, format="mp3")
    print('Hello World 1')


def get_file_name(link):
    # Название файла - ссылка на статью
    file_name = re.split(r'^https?:\/\/?', link)[1]
    for symbols_in_file_name in ['/', '.', '-']:
        # Замена символов в названии файла на '_', чтобы сохранить файл в OS
        file_name = file_name.replace(symbols_in_file_name, '_')
    file_name = os.path.join(os.getcwd(), file_name +'.mp3')  # Сохраняем файл изначально в mp3 формате
    return file_name
