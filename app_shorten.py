from PyQt6 import QtWidgets, QtCore, QtGui, uic
import os
import sys
import shutil
from models import Product, engine, User
from sqlalchemy import select, and_

user = "user"

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("./UI/login.ui", self)

        self.login_btn.clicked.connect(self.login)
        self.guest_btn.clicked.connect(self.guest_login)

    def login(self):
        global user
        login = self.login_edit.toPlainText()
        password = self.password_edit.toPlainText()

        with engine.begin() as conn:
            result = conn.execute(select(User).where(and_(User.c.login == login, User.c.password == password))).fetchone()

            if result is not None:
                user = result[1]

                self.mainWindow = MainWindow(self)
                self.hide()
                self.mainWindow.show()

    def guest_login(self):
        global user
        user = "Авторизованный пользователь"

        self.mainWindow = MainWindow(self)
        self.hide()
        self.mainWindow.show()

class EditWindow(QtWidgets.QMainWindow):
    saved = QtCore.pyqtSignal()
    def __init__(self, id):
        super().__init__()

        uic.loadUi("./UI/edit.ui", self)
        self.id = id
        with engine.begin() as conn:
            product = conn.execute(select(Product).where(Product.c.id == self.id)).fetchone()

        print(product)



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow):
        super().__init__()

        self.win = win

        uic.loadUi("./UI/main.ui", self)

        self.logout_btn.clicked.connect(self.logout)

        self.reload_products()

    def logout(self):
        global user
        user = None

        self.close()
        self.win.show()

    def reload_products(self):
        with engine.begin() as conn:
            products = conn.execute(select(Product)).fetchall()


        for (
            id,
            article,
            title,
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
            product_widget = uic.loadUi("./UI/product.ui")

            product_widget.category.setText(f"<b>{category}</b>")
            product_widget.title.setText(f"<b>{title}</b>")
            product_widget.description.setText(description)
            product_widget.producer.setText(producer)
            product_widget.supplier.setText(supplier)
            
            price_text = ""
            if discount != 0:
                price_text = f"Цена: <s style=\"color: red\">{price}</s> {round((price * (100-discount)/100), 2)}"
            else:
                price_text = f"Цена: {price}"

            product_widget.price.setText(price_text)
            product_widget.measure_type.setText(measure_type)
            product_widget.quantity.setText(str(quantity))
            if quantity == 0:
                product_widget.quantity.setStyleSheet("color: blue")

            product_widget.discount.setText(f"{discount}%")
            if discount > 15:
                product_widget.discount.setStyleSheet("color: #2E8B57")

            if image_url is None:
                image_url = "import/picture.png"
            pixmap = QtGui.QPixmap(image_url)
            product_widget.photo.setPixmap(pixmap.scaled(300, 200))

            product_widget.setProperty("id", id)

            product_widget.mousePressEvent = lambda event, w=product_widget: self.product_clicked(event, w)

            self.product_layout.addWidget(product_widget)

    def product_clicked(self, event, w):
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return

        if user == "Авторизованный пользователь":
            return

        id = w.property("id")

        self.editWindow = EditWindow(id=id)
        self.editWindow.saved.connect(self.reload_products)
        self.editWindow.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main = LoginWindow()
    main.show()

    app.exec()
