from PyQt6 import QtWidgets, QtGui, QtCore, uic
from sqlalchemy import select, and_, update, or_
from models import engine, Product, User
import sys



class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("./UI/login.ui", self)
        self.setWindowTitle("Окно входа")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))

        self.login_btn.clicked.connect(self.login)
        self.guest_btn.clicked.connect(self.guest_login)


    def login(self):
        login = self.login_edit.toPlainText()
        password = self.password_edit.toPlainText()

        with engine.begin() as conn:
            result = conn.execute(select(User).where(and_(User.c.login == login, User.c.password == password))).fetchall()

        if len(result) > 0:
            
            if(result[0][1] == "Администратор" or result[0][1] == "Менеджер"):
                global user
                user = "admin"
                
                self.hide()
                self.mainWindow = MainWindow(self)
                self.mainWindow.show()

        else:
            self.login_error.setText("Ошибка входа")

    def guest_login(self):
        global user
        user = "user"
        self.hide()
        self.mainWindow = MainWindow(self)
        self.mainWindow.show()



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow):
        super().__init__()
        uic.loadUi("./UI/main.ui", self)
        self.setWindowTitle("Каталог")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))

        self.sort = 0
        self.win = win

        if user == "user":
            self.sort_btn.hide()
            self.search_field.hide()
            self.filter_box.hide()


        self.logout_btn.clicked.connect(self.logout)

        self.filter_box.activated.connect(self.reload_products)

        self.sort_btn.clicked.connect(self.switch_sort)

        self.search_field.textChanged.connect(self.reload_products)

        self.reload_products()

    def switch_sort(self):
        self.sort += 1
        if self.sort > 2:
            self.sort = 0
        self.reload_products()

    def logout(self):
        self.hide()
        self.win.show()

    def reload_products(self):
        product_layout: QtWidgets.QVBoxLayout = self.product_layout

        while product_layout.count():
            item = product_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search = self.search_field.toPlainText()
        search_func = or_(
            Product.c.title.ilike(f"%{search}%"),
            Product.c.category.ilike(f"%{search}%"),
            Product.c.producer.ilike(f"%{search}%"),
            Product.c.supplier.ilike(f"%{search}%")
        )

        with engine.begin() as conn:
            if self.sort == 0:
                order = Product.c.id
            elif self.sort == 1:
                order = Product.c.quantity.asc()
            elif self.sort == 2:
                order = Product.c.quantity.desc()


            if self.filter_box.currentText() == "Все поставщики":
                products = conn.execute(select(Product).where(search_func).order_by(order)).fetchall()
            else:
                products = conn.execute(select(Product).where(and_(Product.c.supplier == self.filter_box.currentText(), search_func)).order_by(order)).fetchall()
            suppliers = conn.execute(select(Product.c.supplier).group_by(Product.c.supplier)).fetchall()

        current_supplier = self.filter_box.currentText()

        self.filter_box.clear()
        self.filter_box.addItem("Все поставщики")

        for supplier in suppliers:
            self.filter_box.addItem(supplier[0])

        index = self.filter_box.findText(current_supplier)
        if index != -1:
            self.filter_box.setCurrentIndex(index)





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
            product = uic.loadUi("./UI/product.ui")

            product.title.setText(f"<b>{title}</b>")
            product.category.setText(f"<b>{category}</b>")
            product.title.setWordWrap(True)
            product.category.setWordWrap(True)

            product.measure_type.setText(measure_type)

            price_text = (
            f"Цена: <s style='color:red;'>{price}</s> "
            f"{round(price * (100 - discount) / 100, 2)}<br>"
            if discount != 0
            else f"Цена: {price}<br>"
            )

            product.price.setText(price_text)




            product.supplier.setText(supplier)
            product.producer.setText(producer)
            product.discount.setText(f"{str(discount)}%")
            if discount >= 15:
                product.discount.setStyleSheet("color: #2E8B57")

            product.quantity.setText(str(quantity))
            product.description.setText(description)

            pixmap = QtGui.QPixmap(image_url)
            product.photo.setPixmap(pixmap.scaled(300,200))

            product_layout.addWidget(product)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main = LoginWindow()
    main.show()

    app.exec()