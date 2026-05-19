from PyQt6 import QtWidgets, QtCore, QtGui, uic
from models_practice import engine, User, Product, Order, OrderItem, Delivery
from sqlalchemy import select, and_
import sys
import os

user_name = ""
user_id = 0
user_role = ""

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Окно входа")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))

        uic.loadUi("UI/login.ui", self)

        self.login_btn.clicked.connect(self.login)
        self.guest_btn.clicked.connect(self.guest_login)

    def guest_login(self):
        global user_name
        global user_id
        global user_role

        user_name = "Гость"
        user_id = -1
        user_role = "Гость"

        self.main = MainWindow(self)
        self.hide()
        self.main.show()

    def login(self):
        global user_name
        global user_id
        global user_role


        login = self.login_edit.toPlainText()
        password = self.password_edit.toPlainText()

        with engine.begin() as conn:
            result = conn.execute(select(User).where(and_(User.c.login == login, User.c.password == password))).fetchone()

        if result is not None:
            self.error.setText("")
            user_name = result[2]
            user_id = result[0]
            user_role = result[1]

            self.main = MainWindow(self)
            self.hide()
            self.main.show()
        else:
            self.error.setText("Неверное имя пользователя или пароль")



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow):
        super().__init__()

        self.win = win

        self.setWindowTitle("Список товаров")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))

        uic.loadUi("UI/main.ui", self)

        self.fio.setText(user_name)

        self.reload_products()
        self.logout_btn.clicked.connect(self.logout)

    def logout(self):
        self.hide()
        self.win.show()

    def reload_products(self):
        with engine.begin() as conn:
            products = conn.execute(select(Product)).fetchall()

        for (
            article,
            name,
            measure_type,
            price,
            supplier,
            producer,
            category,
            discount,
            quantity,
            description,
            image_url
        ) in products:
            product_widget = uic.loadUi("UI/product.ui")

            product_widget.category.setText(f"<b>{category}</b>")
            product_widget.title.setText(f"<b>{name}</b>")
            product_widget.category.setWordWrap(True)
            product_widget.title.setWordWrap(True)

            product_widget.description.setText(description)
            product_widget.producer.setText(producer)
            product_widget.supplier.setText(supplier)

            price_text = ""
            if discount != 0:
                price_text = f"<s style='color:red'>{price}</s> {round((price*(100-discount)/100),2)}"
            else:
                price_text = f"{price}"

            product_widget.price.setText(price_text)

            product_widget.measure_type.setText(measure_type)
            product_widget.quantity.setText(str(quantity))

            product_widget.discount.setText(str(discount))
            if discount >= 15:
                product_widget.setStyleSheet("background-color: #2E8B57")

            if quantity == 0:
                product_widget.setStyleSheet("background-color: lightblue")

            if image_url is not None:
                image_url = "import/" + image_url
            else:
                image_url = "import/picture.png"

            pixmap = QtGui.QPixmap(image_url)
            product_widget.photo.setPixmap(pixmap.scaled(300,200))

            self.product_layout.addWidget(product_widget)


if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)

    main = LoginWindow()
    main.show()

    app.exec()