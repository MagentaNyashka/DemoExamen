import traceback
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from sqlalchemy import delete, insert, select, and_, update, or_
from models import engine, Product, User, OrderItem
import sys
import shutil
import os

def Warning(message):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("Подтверждение")
    msg.setText(message)
    msg.setStandardButtons(
        QtWidgets.QMessageBox.StandardButton.Ok |
        QtWidgets.QMessageBox.StandardButton.Cancel
    )

    result = msg.exec()

    return result

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
            global user
            
            if(result[0][1] == "Администратор" or result[0][1] == "Менеджер"):
                user = "admin"
            elif(result[0][1] == "Менеджер"):
                user = "manager"
            
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

class EditWindow(QtWidgets.QMainWindow):
    saved = QtCore.pyqtSignal()
    def __init__(self, id):
        super().__init__()
        uic.loadUi("./UI/edit.ui", self)
        self.setWindowTitle("Редактирование")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))
        self.id = id

        if self.id != -1:
            with engine.begin() as conn:
                result = conn.execute(select(Product).where(Product.c.id == id)).fetchall()

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
            ) in result:
                self.article_edit.setText(article)
                self.title_edit.setText(title)
                self.measure_type_edit.setText(measure_type)
                self.price_edit.setText(str(price))
                self.supplier_edit.setText(supplier)
                self.producer_edit.setText(producer)
                self.category_edit.setText(category)
                self.discount_edit.setText(str(discount))
                self.quantity_edit.setText(str(quantity))
                self.description_edit.setText(description)
                self.image_url_edit.setText(os.path.abspath(image_url))

        else:
            self.delete_btn.hide()

        self.confirm_btn.clicked.connect(self.confirm)
        self.cancel_btn.clicked.connect(self.cancel)
        self.delete_btn.clicked.connect(self.delete)
        

    def confirm(self):
        status = Warning("Сохранить изменения?")

        if status == QtWidgets.QMessageBox.StandardButton.Ok:

            if float(self.price_edit.toPlainText()) < 0:
                Warning("Цена не может быть отрицательной")
                return
            if float(self.discount_edit.toPlainText()) < 0:
                Warning("Скидка не может быть отрицательной")
                return
            if int(self.quantity_edit.toPlainText()) < 0:
                Warning("Количество не может быть отрицательной")
                return




            with engine.begin() as conn:
                try:
                    image = self.image_url_edit.toPlainText()
                    if(image == ""):
                        image = "import/picture.png"
                    else:
                        try:
                            name = image.split("/")

                            base_dir = os.path.dirname(os.path.abspath(__file__))
                            import_dir = os.path.join(base_dir, "import/")

                            full_path = import_dir+name[-1]

                            shutil.copyfile(image, full_path)
                            image = full_path
                        except Exception:
                            Warning("Неверный путь до изображения")
                    if self.id != -1:
                        conn.execute(update(Product).where(Product.c.id == self.id).values(article=self.article_edit.toPlainText(), 
                                                                                   title=self.title_edit.toPlainText(),
                                                                                   measure_type=self.measure_type_edit.toPlainText(),
                                                                                   price=self.price_edit.toPlainText(),
                                                                                   supplier=self.supplier_edit.toPlainText(),
                                                                                   producer=self.producer_edit.toPlainText(),
                                                                                   category=self.category_edit.toPlainText(),
                                                                                   discount=self.discount_edit.toPlainText(),
                                                                                   quantity=self.quantity_edit.toPlainText(),
                                                                                   description=self.description_edit.toPlainText(),
                                                                                   image_url=image))
                    else:
                        conn.execute(insert(Product).values(article=self.article_edit.toPlainText(), 
                                                                                   title=self.title_edit.toPlainText(),
                                                                                   measure_type=self.measure_type_edit.toPlainText(),
                                                                                   price=self.price_edit.toPlainText(),
                                                                                   supplier=self.supplier_edit.toPlainText(),
                                                                                   producer=self.producer_edit.toPlainText(),
                                                                                   category=self.category_edit.toPlainText(),
                                                                                   discount=self.discount_edit.toPlainText(),
                                                                                   quantity=self.quantity_edit.toPlainText(),
                                                                                   description=self.description_edit.toPlainText(),
                                                                                   image_url=image))
                except Exception:
                    traceback.print_exc() 
                    Warning("Данный товар фигурирует в заказе. Отмена")
                    return

            self.saved.emit()
            self.close()
    def cancel(self):
        self.close()

    def delete(self):
        status = Warning("Удалить товар?")

        if status == QtWidgets.QMessageBox.StandardButton.Ok:
            with engine.begin() as conn:
                try:
                    product = conn.execute(select(Product).where(Product.c.id == self.id)).fetchall()

                    conn.execute(delete(Product).where(Product.c.id == self.id))

                    image = product[0][11]
                    name = image.split("/")[-1]
                    if name != "picture.png":
                        os.remove(image)
                except Exception:
                    Warning("Данный товар фигурирует в заказе. Отмена")
                    return

            self.saved.emit()
            self.close()



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
            self.add_btn.hide()



        self.logout_btn.clicked.connect(self.logout)

        self.filter_box.activated.connect(self.reload_products)

        self.sort_btn.clicked.connect(self.switch_sort)

        self.search_field.textChanged.connect(self.reload_products)

        self.add_btn.clicked.connect(self.add_product)

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

            product.setProperty("id", id)
            product.setProperty("article", article)

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

            product.mousePressEvent = lambda event, w=product: self.product_clicked(event, w)

            product_layout.addWidget(product)

    def product_clicked(self, event, product):
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        
        if user == "user":
            return

        id = product.property("id")


        self.editWindow = EditWindow(id=id)
        self.editWindow.saved.connect(self.reload_products)
        self.editWindow.show()
        
    def add_product(self):
        id = -1
        self.editWindow = EditWindow(id=id)
        self.editWindow.saved.connect(self.reload_products)
        self.editWindow.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main = LoginWindow()
    main.show()

    app.exec()