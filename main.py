import sys
from PyQt5 import QtWidgets, uic
from tg import BotThread
from service import Service


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('tg.ui', self)
        self.service = Service("db.sqlite3")
        self.bot_thread = BotThread()
        self.bot_thread.signal.connect(self.onBotHandler)
        self.bot_thread.start()

        self.load_init_data()
        self.cart = []

    def load_init_data(self):
        self.listWidget_clients.clear()
        self.listWidget_goods.clear()

        clients = self.service.get_clients()
        products = self.service.get_products()

        for client in clients:
            self.listWidget_clients.addItem(client[1] + ' ' + client[2])

        for product in products:
            self.listWidget_goods.addItem(product[1] + ' ' + str(product[2]))

    def log(self, text):
        self.listWidget_log.addItem(text)

    def onBotHandler(self, data):
        action = data[0]
        message = data[1]

        if action == 'pull_email':
            succes = self.service.add_client(data[4])
            if succes:
                self.log('клиент добавил email')
                self.bot_thread.send_to_user(
                    message, 'электронная почта полученна!')

        if action == 'error':
            self.log(data[2])

        if action == 'pull_username':
            if len(data) == 5:
                success = self.service.add_client(data[2], data[3], data[4])
            else:
                success = self.service.add_client(data[2], data[3])
            if success:
                self.log(f'клиент {data[2]} добавлен в базу')
                self.bot_thread.send_to_user(
                    message, 'данные получены! вы зарегестрированы!')
                self.load_init_data()
            else:
                self.log(f'клиент {data[2]} уже существует')

        if action == 'catalog':
            products = self.service.get_products()
            self.listWidget_log.addItem(
                'Пользователю ' + message.from_user.username + ' Выдан список товаров')
            all_products = ''
            for product in products:
                all_products += str(product[0]) + ': ' + \
                    str(product[1]) + ' Цена: ' + str(product[2]) + '\n'

            self.bot_thread.send_to_user(message, all_products)

        if action == 'order':
            products = self.service.get_products()
            goods_list = []
            ids = {}
            for product in products:
                goods_list.append(product[1] + ' ' + str(product[2]))
                ids[product[1] + ' ' + str(product[2])] = product[0]
            print(goods_list)
            self.bot_thread.send_keyboard_order(message, goods_list, ids)

        if action == 'good':
            good_id = data[2]
            good_name = data[3]
            self.listWidget_log.addItem(
                'пользователь выбрал товар ' + good_id + ' ' + good_name)
            self.cart.append(int(good_id))

        if action == 'end':
            self.service.add_order(data[2], self.cart)
            self.cart.clear()
            self.bot_thread.send_to_user(message, 'Ваш заказ принят!')
            self.log(f'Пользователь {data[2]} завершил заказ')

        if action == 'cart1':
            if self.cart:
                self.bot_thread.send_to_user(
                    message, self.service.get_cart(self.cart))
            else:
                self.bot_thread.send_to_user(message, 'корзина пуста')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
