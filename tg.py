import re
import time
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from service import Service
from PyQt5.QtCore import QThread, pyqtSignal


bot = telebot.TeleBot('7993481741:AAFsG51Q3J-YCR9RJFSd6YmsSKvBdoHJPT8')
serv = Service("db.sqlite3")


class BotThread(QThread):
    signal = pyqtSignal(list)

    def __init__(self,):
        super().__init__()
        self.current_username = None

    def run(self):
        @bot.message_handler(commands=['start'])
        def start_handler(message):
            bot.send_message(
                message.chat.id, "Привет, добро пожаловать в наш сервис! Пожалуйста введите свой номер.")
            bot.register_next_step_handler(message, on_handle_phone_number)

        @bot.message_handler(content_types=['text'])
        def handle_text(message):
            pass

        def on_handle_phone_number(message):
            phone = message.text
            validate_phone = validate_phone_number(phone)
            if not validate_phone:
                self.signal.emit(['error', message, 'номер телефона неверный'])
                bot.send_message(
                    message.chat.id, 'номер телефона записан неправильно, попробуйте снова.')
                bot.register_next_step_handler(message, on_handle_phone_number)
                return
            try:
                username = message.from_user.username
                keyboard = ReplyKeyboardMarkup()
                btn_skip = KeyboardButton('Пропустить')
                keyboard.add(btn_skip)
                bot.send_message(
                    message.chat.id, 'Если у вас есть электронная почта вы можете ее ввести или не вводить', reply_markup=keyboard)
                bot.register_next_step_handler(
                    message, on_mail, username, validate_phone)
                return
            except Exception:
                self.signal.emit(
                    ['error', message, 'У пользователя не указан username!'])
                return
            time.sleep(0.2)
            on_menu(message)

        def on_mail(message, username, validate_phone):
            email = message.text
            if email == 'Пропустить':
                self.signal.emit(
                    ['pull_username', message, username, validate_phone])
                on_menu(message)
                return
            email = validate_email(email)
            if not email:
                self.signal.emit(
                    ['error', message, 'электронная почта неверна'])
                bot.send_message(
                    message.chat.id, 'элктроннная почта записана неправильно, попробуйте снова.')
                bot.register_next_step_handler(
                    message, on_mail, username, validate_phone)
                return

            self.signal.emit(
                ['pull_username', message, username, validate_phone, email])
            on_menu(message)

        def prettify_number(phone):
            phone = phone.replace(' ', '').replace(
                '(', '').replace(')', '').replace('-', '')
            return phone

        def validate_phone_number(phone):
            if re.match(r'8 ?\(?\d{3}\)? ?\d{3}[ -]?\d{2}[ -]?\d{2}', phone):
                return prettify_number(phone)
            return None

        def validate_email(email):
            if re.match(r'[a-zA-Z0-9._%+-]+@[a-z]+\.[a-z]{2,}', email):
                return email
            return None

        def on_menu(message):
            markup = InlineKeyboardMarkup()
            catalog_btn = InlineKeyboardButton(
                'каталог товаров', callback_data="catalog")
            order_btn = InlineKeyboardButton(
                'сделать заказ', callback_data=f"order: {message.from_user.username}")

            markup.add(catalog_btn)
            markup.add(order_btn)

            bot.send_message(
                message.chat.id, 'выберите действия', reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):

            if call.data == "catalog":
                self.signal.emit(['catalog', call.message])
            if 'order' in call.data:
                order, username = call.data.split(': ')
                self.current_username = username
                self.signal.emit(['order', call.message])
            if 'good' in call.data:
                good, id, good_name = call.data.split('_')
                self.signal.emit(['good', call.message, id, good_name])
            if call.data == 'end':
                self.signal.emit(['end', call.message, self.current_username])
            if call.data == 'cart1':
                self.signal.emit(['cart1', call.message])

        def on_order(message):
            pass

        bot.polling()

    def send_to_user(self, message, data):
        bot.send_message(message.chat.id, data)

    def send_keyboard_order(self, message, goods_list, ids):
        markup = InlineKeyboardMarkup()
        for good in goods_list:
            good_btn = InlineKeyboardButton(
                good, callback_data="good_" + str(ids[good]) + '_' + good)
            markup.add(good_btn)
        end_btn = InlineKeyboardButton('Завершить заказ', callback_data='end')
        markup.add(end_btn)
        cart1_btn = InlineKeyboardButton(
            'посмотреть корзину', callback_data='cart1')
        markup.add(cart1_btn)
        bot.send_message(message.chat.id, 'заказ', reply_markup=markup)

    def send_cart1(self, message):
        pass
