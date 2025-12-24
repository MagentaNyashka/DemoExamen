from PyQt6 import QtWidgets, QtGui, QtCore
from sqlalchemy import select, and_
from models import engine, Product, User
import sys

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.mainWindow = MainWindow(self)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        self.login_input = QtWidgets.QTextEdit("Введите логин")
        self.password_input = QtWidgets.QTextEdit("Введите пароль")
        self.login_error = QtWidgets.QLabel()
        self.login_btn = QtWidgets.QPushButton("Войти")
        self.guest_btn = QtWidgets.QPushButton("Войти как гость")

        self.login_btn.clicked.connect(self.login)
        self.guest_btn.clicked.connect(self.close)

        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_error)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.guest_btn)


        central_widget.setLayout(layout)

    def close(self):
        self.hide()
        self.mainWindow.show()
    def login(self):
        global user
        login = self.login_input.toPlainText()
        password = self.password_input.toPlainText()
        with engine.begin() as conn:
            result = conn.execute(select(User).where(and_(User.c.login == login, User.c.password == password))).fetchall()
        print(result)
        if len(result) > 0:
            self.close()
        else:
            self.login_error.setText(
                '<span style="color:red;">Ошибка: неверное имя пользователя или пароль</span>'
            )
            self.login_error.setWordWrap(True)


class ProductWidget(QtWidgets.QWidget):
    def __init__(self, product):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()

        self.picture = QtWidgets.QLabel("Фото")
        self.picture.setFixedHeight(160)
        self.picture.setFixedWidth(160)
        pixmap = QtGui.QPixmap(product[11])
        self.picture.setPixmap(pixmap.scaled(160,160))


        self.productLabel = QtWidgets.QLabel(f"<b>{product[2]} | {product[7]}</b><br>"
                            f"Описание товара: {product[10]}<br>"
                            f"Производитель: {product[6]}<br>"
                            f"Поставщик: {product[5]}<br>"
                            f"Цена: <s style=\"color:red;\">{product[4]}</s> {round(product[4]*((100 - product[8])/100), 2)}<br>"
                            f"Единица измерения: {product[3]}<br>"
                            f"Количество на складе: {product[9]}")
        self.productLabel.setWordWrap(True)
        self.productLabel.setFixedWidth(400)

        self.discount = QtWidgets.QLabel(f"{product[8]}%")
        if int(product[8]) >= 15:
            self.discount.setStyleSheet("color: #2E8B57")

        self.layout.addWidget(self.picture)
        self.layout.addWidget(self.productLabel)
        self.layout.addWidget(self.discount)


        self.setLayout(self.layout)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow):
        super().__init__()

        self.enterWindow = win

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        self.title = QtWidgets.QLabel("Список товаров")
        main_layout.addWidget(self.title)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        self.scroll_content = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.scroll_content)

        scroll.setWidget(self.scroll_content)
        main_layout.addWidget(scroll)

        with engine.begin() as conn:
            products = conn.execute(select(Product)).fetchall()

        for product in products:
            self.add_product(product)

        self.back_btn = QtWidgets.QPushButton("Выход")
        self.back_btn.clicked.connect(self.back)

        main_layout.addWidget(self.back_btn)


    def add_product(self, product):
        self.layout.addWidget(ProductWidget(product))

    def back(self):
        self.hide()
        self.enterWindow.show()




app = QtWidgets.QApplication(sys.argv)
window = LoginWindow()
window.show()
app.exec()