from PyQt6 import QtWidgets, QtGui, QtCore
from sqlalchemy import select, and_
from models import engine, Product, User
import sys
# создаём класс, унаследованный от QMainWindow
class LoginWindow(QtWidgets.QMainWindow):
    # конструктор класса
    def __init__(self):
        super().__init__()

        # ссылка на основное окно
        # совет: всё кидайте в self, потому что без него может не заработать, а с self всё нормально
        self.mainWindow = MainWindow(self)

        # создаём и устанавливаем центральный виджет, для подробностей просто загуглите
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # создаём вертикальный layout
        layout = QtWidgets.QVBoxLayout(central_widget)


        # TextEdit = Поле для ввода
        self.login_input = QtWidgets.QTextEdit("Введите логин")
        self.password_input = QtWidgets.QTextEdit("Введите пароль")
        # Label = надпись
        self.login_error = QtWidgets.QLabel()
        # PushButton = кнопка
        self.login_btn = QtWidgets.QPushButton("Войти")
        self.guest_btn = QtWidgets.QPushButton("Войти как гость")

        # подключаем функцию по нажанию на кнопку
        self.login_btn.clicked.connect(self.login)
        self.guest_btn.clicked.connect(self.close)

        # закидываем все объекты в layout для отрисовки(ВАЖЕН ПОРЯДОК)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_error)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.guest_btn)

        # устанавливаем layout для центрального виджета
        central_widget.setLayout(layout)

    def close(self):
        # закрыть окно
        self.hide()
        # открыть окно
        self.mainWindow.show()


    def login(self):
        # устанавливаем глобальную переменную
        global user
        # вытаскиваем чистый текст из поля
        login = self.login_input.toPlainText()
        password = self.password_input.toPlainText()
        # работа с БД
        with engine.begin() as conn:
            # SELECT * FROM User u WHERE u.login = :u AND u.password = :p
            # ВАЖНО использовать and_, так запрос будет обрабатываться корректно, нежели с &
            # .fetchall() кидает все строки в list
            result = conn.execute(select(User).where(and_(User.c.login == login, User.c.password == password))).fetchall()

        # если такая запись была найдена, то список будет больше нуля
        if len(result) > 0:
            # вызываем функцию close()
            self.close()
        else:
            # устанавливаем текст для ошибки. По дэфолту пустой
            self.login_error.setText(
                # через style= делаем красный цвет для ошибки
                '<span style="color:red;">Ошибка: неверное имя пользователя или пароль</span>'
            )
            # помогает обработать html, чтобы не было тегов, а был рендер
            self.login_error.setWordWrap(True)


class ProductWidget(QtWidgets.QWidget):
    def __init__(self, product):
        super().__init__()
        # устанавливаем горизонтальный layout
        self.layout = QtWidgets.QHBoxLayout()

        # делаем текст, на который будем накладывать фото
        self.picture = QtWidgets.QLabel("Фото")
        # задаём ширину и высоту
        self.picture.setFixedHeight(160)
        self.picture.setFixedWidth(160)
        # устанавливаем pixmap из пути в БД
        pixmap = QtGui.QPixmap(product[11])
        # накладываем pixmap на label
        self.picture.setPixmap(pixmap.scaled(160,160))

        # Создаём label для продукта по ТЗ(КОД Том 1)
        self.productLabel = QtWidgets.QLabel(f"<b>{product[2]} | {product[7]}</b><br>"
                            f"Описание товара: {product[10]}<br>"
                            f"Производитель: {product[6]}<br>"
                            f"Поставщик: {product[5]}<br>"
                            f"Цена: <s style=\"color:red;\">{product[4]}</s> {round(product[4]*((100 - product[8])/100), 2)}<br>" if product[8] != 0 else f"Цена: {product[4]}"
                            f"Единица измерения: {product[3]}<br>"
                            f"Количество на складе: {product[9]}")
        # помогает обработать html, чтобы не было тегов, а был рендер
        self.productLabel.setWordWrap(True)
        # устанавливаем ширину, чтобы было красиво
        self.productLabel.setFixedWidth(400)

        # создаём label для скидки
        self.discount = QtWidgets.QLabel(f"{product[8]}%")
        # проверка на цвет скидки
        if int(product[8]) >= 15:
            self.discount.setStyleSheet("color: #2E8B57")

        # добавляем объекты в layout
        self.layout.addWidget(self.picture)
        self.layout.addWidget(self.productLabel)
        self.layout.addWidget(self.discount)

        # устанавливаем layout
        self.setLayout(self.layout)


# вот тут уже начинаются сложности со скроллом
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow):
        super().__init__()

        # сохраняем предыдущее окно для возврата при необходимости
        self.enterWindow = win

        # создаём и устанавливаем центральный виджет
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # создаём основной вертикальный layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # создаём заголовок и добавляем его на основной layout
        self.title = QtWidgets.QLabel("Список товаров")
        main_layout.addWidget(self.title)

        # добавляем скролл зону
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        # создаём пустой контент для скролла
        self.scroll_content = QtWidgets.QWidget()
        # создаём второй layout и связываем с скролл зоной
        self.layout = QtWidgets.QVBoxLayout(self.scroll_content)

        # добавляем к скролл зоне контент(пока пустой)
        scroll.setWidget(self.scroll_content)
        # добавляем скролл зону на основной layout
        main_layout.addWidget(scroll)
        # хуйня какая-то я уволняюсь

        # Пояснение этой хуйни
        # 1. QScrollArea - это просто область, которая может прокручиваться, она не хранит в себе ничего
        # 2. scroll_content - это уже контейнер для других виджетов
        # 3. layout - layout, который управляет scroll_content
        # Вот такую хуйню мне выдала ГПТ'шка, я ей верю
        #         MainWindow
        #  └── central_widget
        #       └── main_layout
        #            └── QScrollArea
        #                 └── scroll_content (QWidget)
        #                      └── QVBoxLayout
        #                           ├── Button
        #                           ├── Label
        #                           └── ...


# ⢰⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼
# ⠀⢿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⠴⠶⠖⠒⠛⣿⣽⡟⠛⠓⠒⠶⠶⢤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠴⣯⠏
# ⠀⠀⢿⣯⣿⠷⣶⣤⡴⣶⣶⣤⠤⠤⣤⣄⡀⠀⣀⡤⠶⠛⠉⠀⠀⠀⠀⠀⠀⠴⠿⣼⠿⠦⠀⠀⠀⠀⠀⠀⠉⠛⠲⢦⣄⣀⣤⣴⠒⣻⣿⣿⢻⣿⣿⣿⠋⣩⣴⠋⠀
# ⠀⠀⠀⠙⠿⣦⣼⣟⢷⣷⢹⣿⣌⣿⡟⢺⣿⠛⠻⣄⠀⠀⠀⠀⢀⣠⣤⠤⠖⠒⠒⠛⠒⠒⠒⠦⠤⣤⣀⠀⠀⢀⣤⠖⠛⢿⣇⠐⡾⣷⣿⡟⢚⣿⣷⣿⠶⠋⠁⠀⠀
# ⠀⠀⠀⠀⠀⠈⠙⠛⠛⠻⠾⢿⣾⣮⣗⣸⣿⣆⠄⠀⠙⣦⡖⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢉⣷⡟⠀⡀⢨⣽⣿⣽⣶⢿⡿⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠛⠉⠙⠻⢿⣷⣶⡂⣸⡟⠓⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠛⣧⣄⣿⣾⣿⡋⠉⠀⠀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠟⠁⠀⠀⠀⣠⠾⣿⣿⣿⣿⡁⠀⠈⢳⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠋⠀⠀⣿⣿⣿⣫⣶⠟⢦⡀⠀⠀⣀⠹⣆⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⢀⡼⢿⡷⣾⠀⢀⡞⠁⠀⠹⡄⢻⣿⣿⡆⠀⠘⣿⣦⣤⣀⣀⠀⠀⣀⣀⣤⣶⣿⡯⠀⢀⣾⣿⡿⠋⢀⡞⠀⠀⠙⢆⣀⣿⣻⣯⣷⡀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⢀⡾⠷⠛⢳⡞⣻⠋⠀⠀⠀⠀⢳⡀⢻⣿⣿⣦⣠⣿⡯⣷⡉⣽⠿⠿⠟⠉⣹⡯⣿⣷⣤⣾⣿⣿⠁⠀⣼⠃⠀⠀⠀⠈⠻⡍⠏⠁⠉⢷⡀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⢀⡾⠁⠀⠀⠈⡱⠁⠀⠀⠀⠀⠀⠈⢷⠈⣿⣿⣿⠟⣿⣇⡝⣮⡈⠀⠀⠀⣴⡟⠀⢿⡟⢿⣻⣿⣇⠀⣰⠇⠀⠀⠀⠀⠀⠀⠙⡄⠀⠀⠀⢿⡀⠀⠀⠀
# ⠀⠀⠀⠀⠀⣼⠇⠀⠀⠀⡼⠃⠀⠀⠀⣀⣀⣠⣤⣼⠿⣿⢿⠃⣰⠋⠈⠁⢻⡙⢶⣴⠟⣹⠃⠀⠀⠱⡄⢹⣿⣟⠲⢿⠤⠤⣤⣤⣀⡀⠀⠀⠸⡆⠀⠀⠈⣧⠀⠀⠀
# ⠀⠀⠀⠀⢠⡏⠀⠀⠀⣰⣃⣤⠖⠋⣉⡡⢆⣠⠟⠁⣼⣿⡿⢸⣇⠶⠊⠀⢸⣷⠛⠉⢳⣿⠀⠀⠐⢶⠹⡌⣿⡿⣆⠈⠱⢦⡐⠦⣄⣉⣙⣶⣄⣹⡀⠀⠀⢸⡇⠀⠀
# ⠀⠀⠀⠀⣾⠀⠀⢰⣶⣿⣿⣿⡿⢿⣥⣶⣟⣁⣠⣞⣽⠟⡇⢸⣿⡀⣀⡴⠋⢹⡄⠀⣸⣉⣻⣦⣄⣸⣰⡇⣿⢹⣮⣷⣤⣤⣿⠿⠞⣛⣿⣿⣿⣿⡿⠂⠀⠀⢿⠀⠀
# ⠀⠀⠀⠀⡟⠀⠀⠀⢹⠋⠳⢿⣿⣷⡶⠦⢭⣽⣾⣿⡟⠰⢷⣘⣿⠁⠿⠋⠉⠙⣿⠉⡿⠉⠉⠉⠏⢩⣿⢠⣟⣐⣿⣿⢷⣾⣷⣒⣩⣿⠿⠟⠉⠀⢱⠀⠀⠀⢸⠀⠀
# ⠀⠀⠀⢠⡇⠀⠀⠀⢸⠀⠀⠀⠈⠙⠻⠿⢿⣿⣿⣿⡟⣠⣾⣳⣽⣷⣦⢠⠄⣖⢹⣿⠃⠃⠠⠂⣰⣿⣿⢿⣧⣄⣻⣿⣿⣛⠟⠛⠋⠀⠀⠀⠀⠀⢸⡄⠀⠀⢸⡇⠀
# ⠀⠀⠀⢸⡇⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⢀⣸⠿⠋⢻⣿⣿⣿⣿⡽⣽⣾⣿⣦⣬⠞⠏⠀⢤⣼⣿⣿⣿⢱⣿⣿⣿⣿⡆⠈⠙⠲⣤⡀⠀⠀⠀⠀⠀⢸⡇⠀⠀⢸⡇⠀
# ⠀⠀⠀⠀⡇⢰⣄⣤⣾⠀⠀⠀⢀⣠⠶⠋⠁⠀⢀⣾⣿⢿⣿⣾⣇⢹⡏⣻⣿⠞⠀⠀⠀⠰⣿⣏⣸⡇⣾⣿⣿⣿⣿⣿⠀⠀⠀⠀⠙⠳⢦⣀⠀⠀⢸⢳⣦⡞⢸⡇⠀
# ⠀⠀⠀⠀⣷⡼⣯⡽⢿⣆⣤⣞⣋⣀⣀⣀⣀⣀⣸⣿⣿⣧⠬⠹⣯⣬⣿⠉⠹⣄⠀⠀⠀⣰⠏⠉⣿⢤⣿⠟⠲⣾⣿⣻⣧⣤⣤⣤⡤⠤⠤⠽⠿⢦⡼⠛⣷⠛⢿⠀⠀
# ⠀⠀⠀⠀⢻⡄⠘⠃⠀⢿⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣷⣄⠀⢻⣿⠏⢦⠀⠈⠐⠀⠸⡁⠀⡟⠙⣿⠟⠀⣠⣾⣿⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⠙⢀⡿⠀⠀
# ⠀⠀⠀⠀⠘⣇⠀⠀⠀⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣷⣄⠿⣄⠈⢿⡆⠀⠀⠀⢴⡿⠀⣠⠟⣠⣾⣿⢿⡽⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠀⠀⠀⣸⠇⠀⠀
# ⠀⠀⠀⠀⠀⢹⡆⠀⠀⠀⠘⣆⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⢿⣶⡈⢦⢸⡇⠀⢠⠀⢸⡇⠐⢁⣼⣿⢿⣯⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⠀⠀⢠⡏⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⠀⠘⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢶⣿⣿⣳⠀⠀⡇⠀⣼⠀⢸⡇⠀⣜⣿⣹⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⠁⠀⠀⢀⡿⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⠀⠈⢣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣯⡃⢸⡇⠀⢹⠂⠈⡇⠀⣿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞⠀⠀⠀⢠⡞⠁⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠹⣆⠀⠀⠀⠀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣽⠷⣼⠃⠀⠀⠀⠀⢷⡰⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⣠⠟⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⠀⠀⠀⠀⠙⢦⣀⠀⠀⠀⠀⠀⠀⠀⢿⣴⣿⣦⣀⣠⣀⣤⣿⣧⢾⠆⠀⠀⠀⠀⠀⠀⠀⣠⠶⠃⠀⠀⠀⢀⡼⠋⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⡀⠀⠀⠀⣆⣉⣷⢦⣀⠀⠀⠀⠀⢸⡜⠿⣷⣿⣿⠿⣽⡿⠛⡞⠀⠀⠀⠀⢀⣠⣴⢊⣁⠀⠀⠀⢀⣴⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⣄⣠⢿⣩⡷⡄⠈⠙⠓⠤⢤⣀⣙⣦⣈⣻⣦⣾⣁⣠⣞⣁⣀⠤⠴⠚⠋⣀⣿⣻⣧⡀⣀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠦⣟⡀⠀⠀⠀⠀⠀⠀⠀⠉⠉⢿⡿⠷⣿⢿⡯⠉⠉⠀⠀⠀⠀⠀⠉⠉⣿⡾⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠶⣄⣀⡀⠀⠀⠀⠀⠀⠙⣶⡿⢸⠇⠀⠀⠀⠀⣀⣠⠴⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠒⠒⠲⢾⣟⡥⠿⠒⠒⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀


        # выбираем все продукты из БД
        with engine.begin() as conn:
            products = conn.execute(select(Product)).fetchall()

        # для каждого продукта выполняем добавление в layout
        for product in products:
            self.add_product(product)

        # создаём кнопку для возврата
        self.back_btn = QtWidgets.QPushButton("Выход")
        self.back_btn.clicked.connect(self.back)

        # добавляем на основной layout
        main_layout.addWidget(self.back_btn)


    def add_product(self, product):
        # добавляем свежесозданный виджет в layout
        self.layout.addWidget(ProductWidget(product))

    def back(self):
        # скрываем текущее окно
        self.hide()
        # открываем новое окно
        self.enterWindow.show()



# так надо
app = QtWidgets.QApplication(sys.argv)
# устанавливаем приветственное окно
window = LoginWindow()
# показываем окно
window.show()
# запускаем "так надо"
app.exec()