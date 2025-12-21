from PyQt6 import QtWidgets, QtGui, QtCore
from sqlalchemy import select
from models import engine, Product
import sys


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        title = QtWidgets.QLabel("Список товаров")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setShowGrid(False)

        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 400)
        self.table.setColumnWidth(2, 120)

        layout.addWidget(self.table)

        with engine.begin() as conn:
            products = conn.execute(select(Product)).fetchall()

        for product in products:
            self.add_product(product)


    def add_product(self, product):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 160)

        photo = QtWidgets.QLabel("Фото")
        pixmap = QtGui.QPixmap(product[11])
        photo.setPixmap(pixmap.scaled(160, 160))
        self.table.setCellWidget(row, 0, photo)
        
        info = QtWidgets.QLabel(
            f"<b>{product[2]} | {product[7]}</b><br>"
            f"Описание товара: {product[10]}<br>"
            f"Производитель: {product[6]}<br>"
            f"Поставщик: {product[5]}<br>"
            f"Цена: {product[4]}<br>"
            f"Единица измерения: {product[3]}<br>"
            f"Количество на складе: {product[9]}"
        )

        if(int(product[8]) != 0):
            info = QtWidgets.QLabel(
                f"<b>{product[2]} | {product[7]}</b><br>"
                f"Описание товара: {product[10]}<br>"
                f"Производитель: {product[6]}<br>"
                f"Поставщик: {product[5]}<br>"
                f"Цена: <s style=\"color:red;\">{product[4]}</s> {round(product[4]*((100 - product[8])/100), 2)}<br>"
                f"Единица измерения: {product[3]}<br>"
                f"Количество на складе: {product[9]}"
        )

        info.setWordWrap(True)
        self.table.setCellWidget(row, 1, info)

        discount = QtWidgets.QLabel(
            f"{int(product[8])}%"
        )
        # discount.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        if product[8] > 15:
            discount.setStyleSheet("color: #2E8B57;")
        self.table.setCellWidget(row, 2, discount)



app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
