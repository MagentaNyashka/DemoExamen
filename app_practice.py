from PyQt6 import QtWidgets, QtGui, QtCore, uic
from models_practice import User, Product, Delivery, Order, OrderItem, engine
from sqlalchemy import select, insert, update, and_, or_
import shutil
import os
import sys

user_id = -1
user_role = "Гость"
user_name = "Гость"




class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("UI/login.ui", self)
        self.setWindowTitle("Авторизация")
        self.icon.setPixmap(QtGui.QPixmap("import/Icon.png"))

        self.login_btn.clicked.connect(self.login)
        self.guest_btn.clicked.connect(self.guest_login)

    def login(self):
        global user_id
        global user_role
        global user_name

        login = self.login_edit.toPlainText()
        password = self.password_edit.toPlainText()

        with engine.begin() as conn:
            user = conn.execute(select(User).where(and_(User.c.login == login, User.c.password == password))).fetchone()

        if user is not None:
            user_id = user[0]
            user_role = user[1]
            user_name = user[2]

            self.error.setText("")


            self.main = MainWindow(self)
            self.main.show()
            self.hide()

        else:
            self.error.setText("Неверное имя пользователя или пароль")
            return


    def guest_login(self):
        global user_id
        global user_role
        global user_name

        user_id = -1
        user_role = "Гость"
        user_name = "Гость"

        self.main = MainWindow(self)
        self.main.show()
        self.hide()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow):
        super().__init__()

        self.win = win
        self.sort = 0

        uic.loadUi("UI/main.ui", self)
        self.setWindowTitle("Список товаров")

        self.fio.setText(user_name)


        if user_role != "Администратор" and user_role != "Менеджер":
            self.search_edit.hide()
            self.supplier_box.hide()
            self.sort_btn.hide()




        self.logout_btn.clicked.connect(self.logout)
        self.sort_btn.clicked.connect(self.sort_active)
        self.search_edit.textChanged.connect(self.reload_products)
        self.supplier_box.activated.connect(self.reload_products)


        self.reload_products()

    def sort_active(self):
        self.sort += 1
        if self.sort > 2:
            self.sort = 0

        self.reload_products()

    def logout(self):
        self.win.show()
        self.hide()

    def reload_products(self):

        search = self.search_edit.toPlainText()

        search_func = or_(
            Product.c.name.ilike(f"%{search}%"),
            Product.c.measure_type.ilike(f"%{search}%"),
            Product.c.supplier.ilike(f"%{search}%"),
            Product.c.producer.ilike(f"%{search}%"),
            Product.c.category.ilike(f"%{search}%"),
            Product.c.description.ilike(f"%{search}%"),
        )

        if self.sort == 0:
            sort_func = Product.c.id
        elif self.sort == 1:
            sort_func = Product.c.quantity.asc()
        elif self.sort == 2:
            sort_func = Product.c.quantity.desc()



        while self.product_layout.count():
            item = self.product_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


        current_supplier = self.supplier_box.currentText()

        with engine.begin() as conn:
            if current_supplier == "Все поставщики" or current_supplier == "":
                products = conn.execute(select(Product).where(search_func).order_by(sort_func)).fetchall()
            else:
                products = conn.execute(select(Product).where(and_(search_func, Product.c.supplier == current_supplier)).order_by(sort_func)).fetchall()


            suppliers = conn.execute(select(Product.c.supplier).distinct()).fetchall()

        self.supplier_box.clear()
        self.supplier_box.addItem("Все поставщики")

        for supplier in suppliers:
            self.supplier_box.addItem(supplier[0])

        self.supplier_box.setCurrentText(current_supplier)

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
            product_widget = uic.loadUi("UI/product.ui")

            product_widget.category.setText(f"<b>{category}</b>")
            product_widget.title.setText(f"<b>{title}</b>")
            product_widget.description.setText(description)
            product_widget.producer.setText(producer)
            product_widget.supplier.setText(supplier)


            price_text = ""
            if discount != 0:
                price_text = f"<s style='color:red'>{price}</s> {round((price - price/100*discount),2)}"
            else:
                price_text = f"{price}"
            product_widget.price.setText(price_text)


            product_widget.measure_type.setText(measure_type)
            product_widget.quantity.setText(str(quantity))

            product_widget.discount.setText(str(discount))

            if discount >= 15:
                product_widget.setStyleSheet("background-color:#2E8B57")

            if quantity == 0:
                product_widget.setStyleSheet("background-color:cyan")



            if image_url is not None and image_url != "":
                product_widget.photo.setPixmap(QtGui.QPixmap("import/"+image_url).scaled(300,200))
            else:
                product_widget.photo.setPixmap(QtGui.QPixmap("import/picture.png").scaled(300,200))

            self.product_layout.addWidget(product_widget)








            

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)

    main = LoginWindow()
    main.show()

    app.exec()