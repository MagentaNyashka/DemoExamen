from PyQt6 import QtWidgets, QtGui, QtCore
from sqlalchemy import select, and_, update
from models import engine, Product, User
import sys


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



# создаём класс, унаследованный от QMainWindow
class LoginWindow(QtWidgets.QMainWindow):
    # конструктор класса
    def __init__(self):
        super().__init__()


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
        self.guest_btn.clicked.connect(self.guest_login)

        # закидываем все объекты в layout для отрисовки(ВАЖЕН ПОРЯДОК)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_error)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.guest_btn)

        # устанавливаем layout для центрального виджета
        central_widget.setLayout(layout)

    def close(self):
        # ссылка на основное окно
        # совет: всё кидайте в self, потому что без него может не заработать, а с self всё нормально
        self.mainWindow = MainWindow(self, self.role)
        # закрыть окно
        self.hide()
        # открыть окно
        self.mainWindow.show()


    def login(self):
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
            if(result[0][1] == "Администратор" or result[0][1] == "Менеджер"):
                self.role = "admin"
            else:
                self.role = "guest"
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

    def guest_login(self):
        self.role = "guest"
        self.close()


class ProductWidget(QtWidgets.QWidget):
    def __init__(self, product, role, main_window):
        super().__init__()
        self.main_window = main_window
        # устанавливаем горизонтальный layout
        self.layout = QtWidgets.QHBoxLayout()
        
        self.product = product

        # делаем текст, на который будем накладывать фото
        self.picture = QtWidgets.QLabel("Фото")
        # задаём ширину и высоту
        self.picture.setFixedHeight(160)
        self.picture.setFixedWidth(160)

        # устанавливаем переменные для удобства
        self.id = product[0]
        self.article = product[1]
        self.title = product[2]
        self.measure_type = product[3]
        self.price = product[4]
        self.supplier = product[5]
        self.producer = product[6]
        self.category = product[7]
        self.discount = product[8]
        self.quantity = product[9]
        self.description = product[10]
        self.image_url = product[11]

        # устанавливаем pixmap из пути в БД
        pixmap = QtGui.QPixmap(self.image_url)
        # накладываем pixmap на label
        self.picture.setPixmap(pixmap.scaled(160,160))

        # Создаём label для продукта по ТЗ(КОД Том 1)
        price_text = (
            f"Цена: <s style='color:red;'>{self.price}</s> "
            f"{round(self.price * (100 - self.discount) / 100, 2)}<br>"
            if self.discount != 0
            else f"Цена: {self.price}<br>"
        )

        self.productLabel = QtWidgets.QLabel(
            f"<b>{self.title} | {self.category}</b><br>"
            f"Описание товара: {self.description}<br>"
            f"Производитель: {self.producer}<br>"
            f"Поставщик: {self.supplier}<br>"
            f"{price_text}"
            f"Единица измерения: {self.measure_type}<br>"
            f"Количество на складе: {self.quantity}"
        )

        # помогает обработать html, чтобы не было тегов, а был рендер
        self.productLabel.setWordWrap(True)
        # устанавливаем ширину, чтобы было красиво
        self.productLabel.setFixedWidth(400)

        # создаём label для скидки
        self.discount_ = QtWidgets.QLabel(f"{self.discount}%")
        # проверка на цвет скидки
        if int(self.discount) >= 15:
            self.discount_.setStyleSheet("color: #2E8B57")



        # добавляем объекты в layout
        self.layout.addWidget(self.picture)
        self.layout.addWidget(self.productLabel)
        self.layout.addWidget(self.discount_)

        if(role == "admin"):
            self.edit_btn = QtWidgets.QPushButton("Редактировать")
            self.layout.addWidget(self.edit_btn)
            self.edit_btn.clicked.connect(self.edit)

        # устанавливаем layout
        self.setLayout(self.layout)

    def edit(self):
        self.editWindow = EditWindow(self.product)
        self.editWindow.saved.connect(self.main_window.reload_products)
        self.editWindow.show()

            


class EditWindow(QtWidgets.QMainWindow):
    saved = QtCore.pyqtSignal()
    # конструктор класса
    def __init__(self, product):
        super().__init__()
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        main_layout = QtWidgets.QVBoxLayout()
        central.setLayout(main_layout)

        # устанавливаем переменные для удобства
        self.id = product[0]
        self.article = product[1]
        self.title = product[2]
        self.measure_type = product[3]
        self.price = product[4]
        self.supplier = product[5]
        self.producer = product[6]
        self.category = product[7]
        self.discount = product[8]
        self.quantity = product[9]
        self.description = product[10]
        self.image_url = product[11]

        self.article_edit = QtWidgets.QTextEdit(self.article)
        self.title_edit = QtWidgets.QTextEdit(self.title)
        self.measure_type_edit = QtWidgets.QTextEdit(self.measure_type)
        self.price_edit = QtWidgets.QTextEdit(str(self.price))
        self.supplier_edit = QtWidgets.QTextEdit(self.supplier)
        self.producer_edit = QtWidgets.QTextEdit(self.producer)
        self.category_edit = QtWidgets.QTextEdit(self.category)
        self.discount_edit = QtWidgets.QTextEdit(str(self.discount))
        self.quantity_edit = QtWidgets.QTextEdit(str(self.quantity))
        self.description_edit = QtWidgets.QTextEdit(self.description)

        main_layout.addWidget(self.article_edit)
        main_layout.addWidget(self.title_edit)
        main_layout.addWidget(self.measure_type_edit)
        main_layout.addWidget(self.price_edit)
        main_layout.addWidget(self.supplier_edit)
        main_layout.addWidget(self.producer_edit)
        main_layout.addWidget(self.category_edit)
        main_layout.addWidget(self.discount_edit)
        main_layout.addWidget(self.quantity_edit)
        main_layout.addWidget(self.description_edit)

        self.confirm_btn = QtWidgets.QPushButton("Сохранить")
        self.confirm_btn.clicked.connect(self.confirm)
        self.cancel_btn = QtWidgets.QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.cancel)

        main_layout.addWidget(self.confirm_btn)
        main_layout.addWidget(self.cancel_btn)


    def confirm(self):
        status = Warning("Сохранить изменения?")

        if status == QtWidgets.QMessageBox.StandardButton.Ok:

            # Добавить проверку ошибок

            with engine.begin() as conn:
                conn.execute(update(Product).where(Product.c.id == self.id).values(article=self.article_edit.toPlainText(), 
                                                                                   title=self.title_edit.toPlainText(),
                                                                                   measure_type=self.measure_type_edit.toPlainText(),
                                                                                   price=self.price_edit.toPlainText(),
                                                                                   supplier=self.supplier_edit.toPlainText(),
                                                                                   producer=self.producer_edit.toPlainText(),
                                                                                   category=self.category_edit.toPlainText(),
                                                                                   discount=self.discount_edit.toPlainText(),
                                                                                   quantity=self.quantity_edit.toPlainText(),
                                                                                   description=self.description_edit.toPlainText()))
            
            self.saved.emit()
            self.close()
    def cancel(self):
        self.hide()




# вот тут уже начинаются сложности со скроллом
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, win: LoginWindow, role):
        super().__init__()

        # сохраняем предыдущее окно для возврата при необходимости
        self.enterWindow = win

        # сохраняем текущую роль
        self.role = role

        self.sort = 0

        # создаём и устанавливаем центральный виджет
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # создаём основной вертикальный layout
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)

        if(self.role == "admin"):
            menu_widget = QtWidgets.QWidget()
            upper_layout = QtWidgets.QHBoxLayout()
            menu_widget.setLayout(upper_layout)

            self.title = QtWidgets.QLabel("Список товаров")
            self.search = QtWidgets.QLineEdit()
            self.search.setPlaceholderText("Поиск...")

            self.sort_btn = QtWidgets.QPushButton("Сортировка")
            self.sort_btn.clicked.connect(self.switch_sort)

            upper_layout.addWidget(self.title)
            upper_layout.addWidget(self.search)
            upper_layout.addWidget(self.sort_btn)

            main_layout.addWidget(menu_widget)



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
        # х#### какая-то я уволняюсь

        # Пояснение этой х####
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


        self.reload_products()

        # создаём кнопку для возврата
        self.back_btn = QtWidgets.QPushButton("Выход")
        self.back_btn.clicked.connect(self.back)

        # добавляем на основной layout
        main_layout.addWidget(self.back_btn)

    def reload_products(self):
        # очистить layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()



        
        # заново загрузить из БД
        with engine.begin() as conn:
            if self.sort == 0:
                products = conn.execute(select(Product).order_by(Product.c.id)).fetchall()
            elif self.sort == 1:
                products = conn.execute(select(Product).order_by(Product.c.quantity.asc())).fetchall()
            elif self.sort == 2:
                products = conn.execute(select(Product).order_by(Product.c.quantity.desc())).fetchall()


        for product in products:
            self.add_product(product)

    def add_product(self, product):
        # добавляем свежесозданный виджет в layout
        self.layout.addWidget(ProductWidget(product, self.role, self))

    def back(self):
        # скрываем текущее окно
        self.hide()
        # открываем новое окно
        self.enterWindow.show()

    def switch_sort(self):
        self.sort += 1
        if(self.sort > 2):
            self.sort = 0
        self.reload_products()


# так надо
app = QtWidgets.QApplication(sys.argv)
# устанавливаем приветственное окно
window = LoginWindow()
# показываем окно
window.show()
# запускаем "так надо"
app.exec()