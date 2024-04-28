from telebot.handler_backends import State, StatesGroup


class MyStates(StatesGroup):
    any = State()
    year = State()
    key = State()
