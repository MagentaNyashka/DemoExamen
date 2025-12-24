import sys
from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, Qt, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLabel,
    QScrollArea,
    QHBoxLayout
)
from sqlalchemy.orm import joinedload

from models import User, Session, Product

user: Optional[User] = None


class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        central_widget = QWidget()
        self.mainWindow = MainWindow(self)
        self.setCentralWidget(central_widget)
        self.form = QVBoxLayout()

        self.loginInput = QTextEdit("Ввести логин")
        self.passwordInput = QTextEdit("Ввести пароль")
        self.authBtn = QPushButton("Войти")
        self.guestBtn = QPushButton("Зайти как гость")
        self.authBtn.clicked.connect(self.auth)
        self.guestBtn.clicked.connect(self.close)

        self.form.addWidget(self.loginInput)
        self.form.addWidget(self.passwordInput)
        self.form.addWidget(self.authBtn)
        self.form.addWidget(self.guestBtn)

        central_widget.setLayout(self.form)
        self.setWindowTitle("Вход")
        self.setWindowIcon(QIcon("./import/icon.png"))

    def close(self):
        self.hide()
        self.mainWindow.show()

    def auth(self):
        global user

        login = self.loginInput.toPlainText()
        password = self.passwordInput.toPlainText()

        with Session() as session:
            user = session.query(User).filter_by(login=login, password=password).first()
            if not user:
                return print("failed")
            self.close()


class QProductWidget(QWidget):
    def __init__(self, product: Product):
        super().__init__()
        self.mainLayout = QHBoxLayout()
        image = QPixmap(f"./import/{product.photo or 'picture.png'}")
        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(image.scaled(QSize(100, 100)))
        self.imageLabel.setStyleSheet("width: 100px;")
        self.layout = QVBoxLayout()
        self.nameLabel = QLabel(f"{product.category} | {product.name}")
        self.nameLabel.setStyleSheet('font-weight: bold;')
        self.descriptionLabel = QLabel(f"Описание: {product.description}")
        self.manufacturerLabel = QLabel(f"Производитель: {product.manufacturer.name}")
        self.supplierLabel = QLabel(f"Поставщик: {product.supplier.name}")
        if not product.discount:
            self.priceLabel = QLabel(f"Цена: {product.price} руб.")
        else:
            self.priceLabel = QLabel(
                f"Цена: <s style='color: red'>{product.price}</s> "
                f"<span style='color: black'>{product.fixed_price}</span> руб."
            )
        self.measureLabel = QLabel(f"Единица измерения: {product.measure_type}")
        self.quantityLabel = QLabel(f"Количество на складе: {product.quantity}")
        if not product.quantity:
            self.quantityLabel.setStyleSheet('background-color: #4444AA;')
        for label in [
            self.nameLabel, self.descriptionLabel, self.manufacturerLabel,
            self.supplierLabel, self.priceLabel, self.measureLabel, self.quantityLabel
        ]:
            self.layout.addWidget(label)
        self.mainLayout.addWidget(self.imageLabel)
        self.mainLayout.addLayout(self.layout)
        if product.discount:
            self.discountLabel = QLabel(f"Действующая скидка: {product.discount}%")
            self.mainLayout.addWidget(self.discountLabel)
        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setStyleSheet((
            'background-color: #2E8B57' if product.discount else ''
        ))


class MainWindow(QMainWindow):
    def __init__(self, win: AuthWindow):
        super().__init__()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.enterWindow = win
        self.view = QVBoxLayout()
        with Session() as session:
            products = session.query(Product).options(
                joinedload(Product.manufacturer), joinedload(Product.supplier)
            ).all()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        productContent = QWidget()
        scrollLayout = QVBoxLayout(productContent)
        for product in products:
            scrollLayout.addWidget(QProductWidget(product))
        scroll.setWidget(productContent)
        self.logoutBtn = QPushButton("Выйти")
        self.logoutBtn.clicked.connect(self.logout)

        self.view.addWidget(scroll)
        self.view.addWidget(self.logoutBtn)
        central_widget.setLayout(self.view)
        self.setWindowTitle("Список товаров")
        self.setWindowIcon(QIcon("./import/icon.png"))

    def logout(self):
        global user
        user = None
        self.hide()
        self.enterWindow.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
