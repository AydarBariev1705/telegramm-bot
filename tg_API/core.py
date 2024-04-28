import telebot
from telebot import types
from telebot.types import Message
from telebot import custom_filters
from tg_API.utils.utils import MyStates
from site_API.core import headers, site_api, url
from settings import SiteSettings
from telebot.storage import StateMemoryStorage
from database.common.models import db, History
from database.core import crud


def run_tg_bot() -> None:
    """Основная функция для запуска телеграмм бота.
    URL-адресс бота: https://t.me/Mymoviesdatabasebot"""

    db_write = crud.create()
    db_read = crud.retrieve()
    state_storage = StateMemoryStorage()
    tg = SiteSettings()
    bot = telebot.TeleBot(tg.tg_key.get_secret_value(), state_storage=state_storage)

    @bot.message_handler(state="*", commands=['start'])
    def handle_start(message: Message) -> None:
        """Функция для начала работы бота, которая включает в себя кнопки для работы с ботом"""
        markup_inline = types.InlineKeyboardMarkup(row_width=1)
        item_titles_random = types.InlineKeyboardButton(text='Случайный фильм из 250 лучших.',
                                                        callback_data='random_movie')
        item_upcoming = types.InlineKeyboardButton(text='Список фильмов, которые скоро выйдут.',
                                                   callback_data='upcoming')
        item_titles_year = types.InlineKeyboardButton(text='Список фильмов вышедших в определенном году.',
                                                      callback_data='titles_year')
        item_search_by_keyword = types.InlineKeyboardButton(text='Поиск фильма по ключевому слову.',
                                                            callback_data='search_by_keyword')
        item_history = types.InlineKeyboardButton(text='История запросов.',
                                                  callback_data='history')
        markup_inline.add(item_titles_random, item_upcoming, item_titles_year, item_search_by_keyword, item_history)
        bot.send_message(message.chat.id, 'Доброго времени суток!\nЕсли вы не знаете с чего начать то наберите /help\n'
                                          'Выберите опцию:',
                         reply_markup=markup_inline)

    @bot.message_handler(state="*", commands=['help'])
    def help_info(message: Message) -> None:
        """Функция для обработки команды /help"""

        bot.send_message(message.chat.id,
                         '<b>Случайный фильм из 250 лучших:</b> Пользователь получает один случайный фильм из списка 250 лучших фильмов и его год выпуска.\n'
                         '<b>Список фильмов, которые скоро выйдут:</b> Пользователь получает список фильмов, которые скоро выйдут, и их дату выхода.\n'
                         '<b>Список фильмов вышедших в определенном году.:</b> Данная функция предоставляет список фильмов, вышедших в год выбранный пользователем.\n'
                         '<b>Поиск фильма по ключевому слову:</b> Поиск фильмов по ключевому слову пользователя.\n'
                         '<b>/start:</b> Запустить бота заново.',
                         parse_mode='html')

    @bot.message_handler(state=MyStates.year)
    def user_message(message: Message) -> None:

        """Функция, которая отправляет в чат список фильмов вышедших в определенный год и записывает результат в базу данных"""
        year = message.text.strip().lower()
        movie_by_year = site_api.get_film_by_year()
        response = movie_by_year("GET", url, headers, year, timeout=3)
        bot.send_message(message.chat.id, response)
        data = [{"request_name": 'titles_year', "message": response}]
        db_write(db, History, data)

    @bot.message_handler(state=MyStates.key)
    def user_message(message: Message) -> None:

        """Функция, которая отправляет в чат список фильмов по ключевому слову и записывает результат в базу данных"""

        key = message.text.strip().lower()
        movie_by_key = site_api.search_by_keyword()
        response = movie_by_key("GET", url, headers, key, timeout=3)
        bot.send_message(message.chat.id, response)
        data = [{"request_name": 'search_by_keyword', "message": response}]
        db_write(db, History, data)

    @bot.callback_query_handler(state="*", func=lambda call: True)
    def callback(call):

        """Функция, которая обрабатывает нажатия на кнопки в боте и записывает результат в базу данных """

        if call.message:
            if call.data == 'random_movie':
                random_movie = site_api.random_movie()
                response = random_movie(headers)
                bot.send_message(call.message.chat.id, '<b>Ваш случайный фильм:\n</b>' + response,
                                 parse_mode='html')
                data = [{"request_name": 'random_movie', "message": response}]
                db_write(db, History, data)
            elif call.data == 'upcoming':
                upcoming = site_api.upcoming_movies()
                response = upcoming(headers)
                bot.send_message(call.message.chat.id, '<b>Фильмы, которым только предстоит выйти:\n</b>' + response,
                                 parse_mode='html')
                data = [{"request_name": 'upcoming', "message": response}]
                db_write(db, History, data)

            elif call.data == 'titles_year':
                bot.send_message(call.message.chat.id, 'Введите год:')
                bot.set_state(call.message.chat.id, MyStates.year)

            elif call.data == 'search_by_keyword':
                bot.send_message(call.message.chat.id, 'Введите ключевое слово:')
                bot.set_state(call.message.chat.id, MyStates.key)
            elif call.data == 'history':
                retrieved = db_read(db, History, History.request_name, History.message)
                history = ''
                for element in retrieved:
                    history += element.request_name + ': ' + element.message + '\n'
                bot.send_message(call.message.chat.id, f'История запросов:\n {history}')

    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.polling(none_stop=True)


