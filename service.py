import sqlite3


class Service:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_all_tables(self):
        self.cursor.execute("""
            create table clients (
                id integer primary key AUTOINCREMENT,
                username varchar(64) not null,
                phone varchar(14),
                email varchar(20)
            )
        """)

        self.conn.commit()

        self.cursor.execute("""
            create table products (
                id integer primary key autoincrement,
                name varchar(64) not null,
                price integer not null
            )
        """)

        self.conn.commit()

        self.cursor.execute("""
            create table orders (
                id integer primary key autoincrement,
                client_id integer not null references clients(id),
                date_time TIMESTAMP
            )
        """)

        self.conn.commit()

        self.cursor.execute("""
            create table orders_line (
                id integer primary key autoincrement,
                order_id integer not null references orders(id),
                product_id integer not null references products(id),
                quantity integer not null
            )
        """)

        self.conn.commit()

    def _validate_name(self, name):
        """проверка имени пользователя"""
        if name:
            return name
        return None

    def _validate_price(self, price):
        """проверка цены"""
        if price > 0:
            return price
        return None

    def add_client(self, username, phone=None, email=None):
        """добавить клиента"""
        username = self._validate_name(username)
        if phone is None:
            phone = ""
        if email is None:
            email = ""
        try:
            if username is not None:
                self.cursor.execute(
                    f"insert into clients(username, phone, email) values ('{username}', '{phone}', '{email}')")
                self.conn.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def add_product(self, name, price):
        """добавить новый товар"""
        name = self._validate_name(name)
        price = self._validate_price(price) 

        if (name is not None) and (price is not None):
            self.cursor.execute(
                f"insert into products(name, price) values ('{name}', {price})")
            self.conn.commit()

    def new_order(self, username):  
        """создать новый заказ"""
        username = self._validate_name(username)

        if (username is not None):
            self.cursor.execute(
                f"insert into order(username) values ('{username}')")
            self.conn.commit()

    def add_to_order(self, order_id, product_id, quantity=1):
        """добавление товаров в заказ"""
        order_id = self._validate_name(order_id)
        product_id = self._validate_name(product_id)

        if (order_id is not None) and (product_id is not None):
            self.cursor.execute(
                f"insert into order(order_id, product_id, quanyity) values ('{order_id}', '{product_id}', {quantity})")
            self.conn.commit()

    
    def get_client_orders(self, username):
        self.cursor.execute("select * from orders_line")
        orders_line = self.cursor.fetchall()

        return orders_line

    def get_clients(self):
        """получение информации о клиенте"""
        self.cursor.execute("select * from clients")
        clients = self.cursor.fetchall()

        return clients

    def get_products(self):
        """получение информации о товарах"""
        self.cursor.execute("select * from products")
        products = self.cursor.fetchall()

        return products

    def get_orders(self):
        """получение заказов из базы"""
        self.cursor.execute("""select o.id, o.date_time, c.username, c.phone
                                    from orders o
                                    join clients c on o.client_id = c.id""")

        orders = self.cursor.fetchall()

        return orders

    def add_order(self, username, cart):
        """добавление заказа"""
        order_line = {}
        for good_id in cart:
            if good_id in order_line:
                order_line[good_id] += 1
            else:
                order_line[good_id] = 1
        self.cursor.execute(
            f'select id from clients where username = "{username}"')
        user_id = self.cursor.fetchone()[0]
        print(user_id)
        self.cursor.execute(
            f"insert into orders(client_id) values ({user_id})")
        order_id = self.cursor.lastrowid
        self.conn.commit()
        print(order_id)
        for good_id in order_line:
            self.cursor.execute(
                f'insert into orders_line(order_id,product_id,quantity) values ({order_id}, {good_id}, {order_line[good_id]})')
            self.conn.commit()

    def get_cart(self, cart):
        """выдать корзину"""
        self.cursor.execute(
            f"select * from products where id in ({','.join(list(map(str, cart)))})")
        products_cart = self.cursor.fetchall()
        order_line = {}
        for good_id in cart:
            if good_id in order_line:
                order_line[good_id] += 1
            else:
                order_line[good_id] = 1
        for good_id in order_line:
            for product in products_cart:
                if product[0] == good_id:
                    order_line[good_id] = f'{product[1]} {order_line[good_id]}'
        return '\n'.join(list(order_line.values()))
