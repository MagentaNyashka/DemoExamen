from PyQt6 import QtWidgets, QtCore, QtGui, uic
from PyQt6.QtWidgets import QFileDialog
from models_reference import engine, User, Product, Order, OrderItem, Delivery
from sqlalchemy import and_, delete, select, insert, update, or_
import sys
import os
import shutil

user_name = ""
user_id = 0
user_role = ""


def Warning(type, message):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(type)
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

        self.setWindowTitle("Окно входа")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))


        uic.loadUi("UI/login.ui", self)

        pixmap = QtGui.QPixmap("import/Icon.png")
        self.icon.setPixmap(pixmap.scaled(300,200))

        self.login_btn.clicked.connect(self.login)
        self.guest_btn.clicked.connect(self.guest_login)

    def login(self):
        global user_name
        global user_id
        global user_role

        username = self.login_edit.toPlainText()
        password = self.password_edit.toPlainText()

        with engine.begin() as conn:
            result = conn.execute(select(User).where(and_(User.c.login == username, User.c.password == password))).fetchone()

        if result is not None:
            user_id = result[0]
            user_role = result[1]
            user_name = result[2]

            self.main = MainWindow(self)
            self.hide()
            self.main.show()

        else:
            self.error.setText("Неверный логин или пароль")

    def guest_login(self):
        global user_name
        global user_id
        global user_role

        user_name = "Гость"
        user_id = -1
        user_role = "Авторизованный пользователь"

        self.main = MainWindow(self)
        self.hide()
        self.main.show()



# ВАЖНО!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ЗДЕСЬ УБОГИЙ НО РАБОЧИЙ ВАРИАНТ ДОБАВЛЕНИЯ ИЗОБРАЖЕНИЙ,
# МНЕ ОН НЕ НРАВИТЬСЯ, СКОРЕЕ ВСЕГО Я БУДУ ИСПОЛЬЗОВАТЬ
# МЕТОД ИЗ app_ui.py

class AddProduct(QtWidgets.QMainWindow):
    saved = QtCore.pyqtSignal()

    def __init__(self, id):
        super().__init__()

        self.id = id

        uic.loadUi("UI/edit.ui", self)
        
        if user_role != "Администратор":
            self.image_btn.hide()
            self.delete_btn.hide()
        if self.id != -1:
            self.article.hide()
            self.article_edit.hide()
        else:
            self.delete_btn.hide()

       
        self.file_path = None
        self.destination_path = None
        self.old_image = None
        self.selected_image = None

        self.image_pixmap.setPixmap(QtGui.QPixmap("import/picture.png").scaled(300,200))

        self.setWindowTitle("Добавление товара")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))

        self.image_btn.clicked.connect(self.open_file_dialog)

        self.confirm_btn.clicked.connect(self.confirm)
        self.cancel_btn.clicked.connect(self.close)
        self.delete_btn.clicked.connect(self.delete_product)



        with engine.begin() as conn:
            producer_list = conn.execute(select(Product.c.producer).distinct()).fetchall()
            category_list = conn.execute(select(Product.c.category).distinct()).fetchall()

            self.producer_box.addItems([item[0] for item in producer_list])
            self.category_box.addItems([item[0] for item in category_list])

        if self.id != -1:
            self.load_data()

    def delete_product(self):
        result = Warning("Подтверждение", "Вы уверены, что хотите удалить товар?")

        try:
            if result ==  QtWidgets.QMessageBox.StandardButton.Ok:
                print(self.id)
                print(self.old_image)
                with engine.begin() as conn:
                    conn.execute(delete(Product).where(Product.c.id == self.id))
                os.remove("import/"+self.old_image)
        except Exception as e:
            print(e)
            Warning("Ошибка", "Товар фигурирует в заказе")

        self.saved.emit()
        self.close()


    def load_data(self):
        with engine.begin() as conn:
            product = conn.execute(
                select(Product).where(Product.c.id == self.id)
            ).fetchone()

        self.article_edit.setText(product[1])
        self.title_edit.setText(product[2])
        self.measure_type_edit.setText(product[3])
        self.price_edit.setText(str(product[4]))
        self.supplier_edit.setText(str(product[5]))
        self.producer_box.setCurrentText(product[6])
        self.category_box.setCurrentText(product[7])
        self.discount_edit.setText(str(product[8]))
        self.quantity_edit.setText(str(product[9]))
        self.description_edit.setText(product[10])

        self.old_image = product[11]
        self.selected_image = product[11]

        if product[11]:
            self.image_pixmap.setPixmap(
                QtGui.QPixmap("import/" + product[11]).scaled(300,200)
            )


    def close(self):
        self.hide()

    def confirm(self):

        try:
            price = float(self.price_edit.toPlainText())
            discount = float(self.discount_edit.toPlainText())
            quantity = int(self.quantity_edit.toPlainText())
        except ValueError:
            Warning("Ошибка", "Введите корректные данные")
            return

        if price < 0:
            Warning("Ошибка", "Цена не может быть отрицательной")
            return

        if discount < 0:
            Warning("Ошибка", "Скидка не может быть отрицательной")
            return

        if quantity < 0:
            Warning("Ошибка", "Количество не может быть отрицательным")
            return

        if self.file_path and self.destination_path:

            if os.path.exists(self.destination_path):

                if os.path.basename(self.destination_path) != self.old_image:
                    Warning(
                        "Ошибка",
                        "Файл с таким именем уже существует"
                    )
                    return

            shutil.copy(self.file_path, self.destination_path)


        with engine.begin() as conn:
            if self.id != -1:
                conn.execute(update(Product).where(Product.c.id == self.id).values(
                                name=self.title_edit.toPlainText(),
                                measure_type=self.measure_type_edit.toPlainText(),
                                price=self.price_edit.toPlainText(),
                                supplier=self.supplier_edit.toPlainText(),
                                producer=self.producer_box.currentText(),
                                category=self.category_box.currentText(),
                                discount=self.discount_edit.toPlainText(),
                                quantity=self.quantity_edit.toPlainText(),
                                description=self.description_edit.toPlainText(),
                                image_url=self.selected_image
                            ))
            else:
                conn.execute(insert(Product).values(
                                article=self.article_edit.toPlainText(), 
                                name=self.title_edit.toPlainText(),
                                measure_type=self.measure_type_edit.toPlainText(),
                                price=self.price_edit.toPlainText(),
                                supplier=self.supplier_edit.toPlainText(),
                                producer=self.producer_box.currentText(),
                                category=self.category_box.currentText(),
                                discount=self.discount_edit.toPlainText(),
                                quantity=self.quantity_edit.toPlainText(),
                                description=self.description_edit.toPlainText(),
                                image_url=self.selected_image
                            ))
                
                if (self.old_image and self.old_image != self.selected_image):
                    old_path = os.path.join(
                        "import",
                        self.old_image
                    )

                    if os.path.exists(old_path):
                        os.remove(old_path)

        self.saved.emit()
        self.hide()

    def open_file_dialog(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if self.file_path:

            destination_folder = "import"

            self.destination_path = os.path.join(
                destination_folder,
                os.path.basename(self.file_path)
            )

            self.selected_image = os.path.basename(self.file_path)

            self.image_pixmap.setPixmap(
                QtGui.QPixmap(self.file_path).scaled(300,200)
            )



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow):
        super().__init__()
        self.win = win
        self.sort = 0

        uic.loadUi("UI/main.ui", self)

        self.setWindowTitle("Список товаров")
        self.setWindowIcon(QtGui.QIcon('import/Icon.ico'))


        if user_role == "Авторизованный пользователь":
            self.search_edit.hide()
            self.sort_btn.hide()
            self.supplier_box.hide()
            self.add_product_btn.hide()

        self.fio.setText(user_name)

        self.logout_btn.clicked.connect(self.logout)

        self.search_edit.textChanged.connect(self.reload_products)

        self.supplier_box.activated.connect(self.reload_products)

        self.sort_btn.clicked.connect(self.switch_sort)

        self.add_product_btn.clicked.connect(self.add_product)

        self.reload_products()

    def add_product(self):
        self.product_window = AddProduct(id=-1)
        self.product_window.saved.connect(self.reload_products)
        self.product_window.show()

    def logout(self):
        self.hide()
        self.win.show()

    def switch_sort(self):
        self.sort += 1
        if self.sort > 2:
            self.sort = 0
        self.reload_products()


    def reload_products(self):

        while self.product_layout.count():
            item = self.product_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search = self.search_edit.toPlainText()
        search_func = or_(
            Product.c.name.ilike(f"%{search}%"),
            Product.c.category.ilike(f"%{search}%"),
            Product.c.description.ilike(f"%{search}%"),
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


            if self.supplier_box.currentText() == "Все поставщики" or self.supplier_box.currentText() == "":
                products = conn.execute(select(Product).where(search_func).order_by(order)).fetchall()
            else:
                products = conn.execute(select(Product).where(and_(Product.c.supplier == self.supplier_box.currentText(), search_func)).order_by(order)).fetchall()
            
            suppliers = conn.execute(select(Product.c.supplier).distinct()).fetchall()

        current_supplier = self.supplier_box.currentText()


        self.supplier_box.clear()
        self.supplier_box.addItem("Все поставщики")

        for supplier in suppliers:
            self.supplier_box.addItem(supplier[0])

        self.supplier_box.setCurrentText(current_supplier)

        for (
            id,
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

            product_widget.setProperty("id", id)

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
            if quantity == 0:
                product_widget.quantity.setStyleSheet("background-color: lightblue")

            product_widget.discount.setText(str(discount))
            if discount >= 15:
                product_widget.discount.setStyleSheet("background-color: #2E8B57")

            if image_url is not None:
                image_url = "import/" + image_url
            else:
                image_url = "import/picture.png"

            pixmap = QtGui.QPixmap(image_url)
            product_widget.photo.setPixmap(pixmap.scaled(300,200))

            product_widget.mousePressEvent = lambda event, w=product_widget: self.product_clicked(event, w)

            self.product_layout.addWidget(product_widget)
            
    def product_clicked(self, event, product):
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        
        if user_role == "Авторизованный пользователь":
            return

        id = product.property("id")


        self.editWindow = AddProduct(id=id)
        self.editWindow.saved.connect(self.reload_products)
        self.editWindow.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main = LoginWindow()
    main.show()
    app.exec()