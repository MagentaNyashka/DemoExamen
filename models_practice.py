<<<<<<< HEAD
from sqlalchemy import select, insert, create_engine, text, MetaData
from datetime import datetime
import openpyxl


host = "localhost"
port = 5432
username = "postgres"
password = "Bghujknmol123"
db = "demo"

engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db}")
=======
from sqlalchemy import create_engine, MetaData, insert, select, text
from datetime import datetime
import openpyxl

host = "localhost"
port = 5432
user = "psychoslvt"
password = "Bghujknmol123"
db = "demo"

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
>>>>>>> fe35492f007fb09b1324d96c656c8981ecd78a8f

metadata = MetaData()
metadata.reflect(bind=engine)

<<<<<<< HEAD
User = metadata.tables["user"]
Delivery = metadata.tables["delivery"]
Order = metadata.tables["order"]
OrderItem = metadata.tables["order_item"]
Product = metadata.tables["product"]


def normalize_article(value: str):
    articles = []
    quantities = []
    raw = [x.strip() for x in value.split(",")]

    for i in range(0, len(raw), 2):
        articles.append(raw[i])
        quantities.append(raw[i+1])
    return articles, quantities

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text('TRUNCATE "user", "delivery", "order_item", "order", "product" CASCADE;'))


=======
User = metadata.tables["User"]
Delivery = metadata.tables["Delivery"]
Order = metadata.tables["Order"]
OrderItem = metadata.tables["OrderItem"]
Product = metadata.tables["Product"]


# def parse_date(value):
#     s = str(value).split()[0]
#     isinstance(value, datetime)
#     for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
#         try:
#             return datetime.strptime(s, fmt).date()
#         except:
#             pass
#     raise ValueError(f"Unknown date format: {value}")

def normalize_article(data: str):
    raw = [x.strip() for x in data.split(',')]
    articles = []
    quantities = []

    for i in range(0, len(raw), 2):
        articles.append(raw[i])
        quantities.append(int(raw[i+1]))

    return articles, quantities


if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text('TRUNCATE "OrderItem" CASCADE; TRUNCATE "Order" CASCADE; TRUNCATE "Product" CASCADE; TRUNCATE "User" CASCADE; TRUNCATE "Delivery" CASCADE;'))
    
>>>>>>> fe35492f007fb09b1324d96c656c8981ecd78a8f
    user_table = openpyxl.load_workbook("import/user_import.xlsx").active

    user_rows = []
    for row in user_table.iter_rows(values_only=True, min_row=2):
        if row[0] is None:
            continue
<<<<<<< HEAD
        user_rows.append({
            "role": row[0],
            "name": row[1],
            "login": row[2],
            "password": row[3]
        })

    with engine.begin() as conn:
        conn.execute(insert(User), user_rows)
    
    with engine.begin() as conn:
        user_map = dict(conn.execute(select(User.c.name, User.c.id).where(User.c.role != "Авторизованный пользователь")).fetchall())
=======
        data = {
            "role": str(row[0]),
            "name": str(row[1]),
            "login": str(row[2]),
            "password": str(row[3])
        }

        user_rows.append(data)

    with engine.begin() as conn:
        conn.execute(insert(User), user_rows)

    with engine.connect() as conn:
        user_map = dict(conn.execute(select(User.c.name, User.c.id).where(User.c.role != "Авторизованный клиент")).fetchall())
>>>>>>> fe35492f007fb09b1324d96c656c8981ecd78a8f

    delivery_table = openpyxl.load_workbook("import/Пункты выдачи_import.xlsx").active

    delivery_rows = []
<<<<<<< HEAD
    for i, row in enumerate(delivery_table.iter_rows(values_only=True, min_row=1)):
        if row[0] is None:
            continue
        delivery_rows.append({
            "id": i+1,
            "address": row[0]
        })

    with engine.begin() as conn:
        conn.execute(insert(Delivery), delivery_rows)
    
    product_table = openpyxl.load_workbook("import/Tovar.xlsx").active

    product_rows = []
    for row in product_table.iter_rows(values_only=True, min_row=2):
        if row[0] is None:
            continue
        product_rows.append({
            "article": row[0],
            "name": row[1],
            "measure_type": row[2],
            "price": row[3],
            "supplier": row[4],
            "producer": row[5],
            "category": row[6],
            "discount": row[7],
            "quantity": row[8],
            "description": row[9],
            "image_url": row[10]
        })
=======
    for i, row in enumerate(delivery_table.iter_rows(values_only=True)):
        if row[0] is None:
            continue
        data = {
            "id": i+1,
            "address": str(row[0])
        }

        delivery_rows.append(data)

    with engine.begin() as conn:
        conn.execute(insert(Delivery), delivery_rows)

    product_table = openpyxl.load_workbook("import/Tovar.xlsx").active

    product_rows = []

    for row in product_table.iter_rows(values_only=True, min_row=2):
        if row[0] is None:
            continue
        data = {
            "article": str(row[0]),
            "title": str(row[1]),
            "measure_type": str(row[2]),
            "price": float(row[3]),
            "supplier": str(row[4]),
            "producer": str(row[5]),
            "category": str(row[6]),
            "discount": float(row[7]),
            "quantity": int(row[8]),
            "description": str(row[9]),
            "image_url": f"import/{str(row[10])}" if row[10] is not None else None
        }

        product_rows.append(data)
>>>>>>> fe35492f007fb09b1324d96c656c8981ecd78a8f

    with engine.begin() as conn:
        conn.execute(insert(Product), product_rows)

<<<<<<< HEAD

    order_table = openpyxl.load_workbook("import/Заказ_import.xlsx").active

    order_rows = []
    order_item_rows = []

    for row in order_table.iter_rows(values_only=True, min_row=2):
        if row[0] is None:
            continue
        
        order_id = row[0]
        article_raw = row[1]
        order_date = row[2]
        delivery_date = row[3]
        delivery_id = row[4]
        user_raw = row[5]
        challenge_code = row[6]
        status = row[7]

        if not isinstance(delivery_date, datetime) or not isinstance(order_date, datetime):
            continue

        order_rows.append({
=======
    order_table = openpyxl.load_workbook("import/Заказ_import.xlsx").active

    orders_rows = []
    order_item_rows = []

    for row in order_table.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue

        try:
            order_id = int(row[0])
            article_raw = str(row[1])
            order_date = row[2]
            delivery_date = str(row[3])
            if not isinstance(order_date, datetime):
                continue
            delivery_id = int(row[4])
            user_id = user_map.get(str(row[5]))
            challenge_code = int(row[6])
            status = str(row[7])
        except:
            continue

        orders_rows.append({
>>>>>>> fe35492f007fb09b1324d96c656c8981ecd78a8f
            "id": order_id,
            "order_date": order_date,
            "delivery_date": delivery_date,
            "address_id": delivery_id,
<<<<<<< HEAD
            "user_id": user_map.get(user_raw),
=======
            "user_id": user_id,
>>>>>>> fe35492f007fb09b1324d96c656c8981ecd78a8f
            "challenge_code": challenge_code,
            "status": status
        })

        articles, quantities = normalize_article(article_raw)
        for a, q in zip(articles, quantities):
            order_item_rows.append({
<<<<<<< HEAD
                "order_id": order_id,
                "article": a,
                "quantity": q
            })

    with engine.begin() as conn:
        conn.execute(insert(Order), order_rows)
        conn.execute(insert(OrderItem), order_item_rows)
        
=======
                "article": a,
                "order": order_id,
                "quantity": q
            })
        
    with engine.begin() as conn:
        conn.execute(insert(Order), orders_rows)
        conn.execute(insert(OrderItem), order_item_rows)
        

    
>>>>>>> fe35492f007fb09b1324d96c656c8981ecd78a8f
