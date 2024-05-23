from typing import List, TypeVar
from .data import *
from .gen import *

def to_str_value(x):
    if x is None:
        return 'NULL'
    elif isinstance(x, str):
        return "'" + x.replace("'", "''") + "'"
    elif isinstance(x, datetime):
        return "'" + str(x) + "'"
    else:
        return str(x)

def insert(connection, objs: List):
    table = objs[0].table_name
    data = list(map(lambda x: x.__dict__, objs))
    for d in data:
        if 'id' in d:
            d.pop('id')
    fields = data[0].keys()
    fields_str = f"({', '.join(fields)})"
    values = map(lambda x: x.values(), data)
    values_str = ', '.join(map(
        lambda x: f"({', '.join(map(to_str_value, x))})",
        values
    ))

    sql = f"INSERT INTO {table} {fields_str} VALUES {values_str}"
    with connection, connection.cursor() as cursor:
        cursor.execute(sql)

def select_all(connection, klass: type[Data]) -> List[Data]:
    table = klass.table_name
    sql = f"SELECT * FROM {table}"
    with connection, connection.cursor() as cursor:
        cursor.execute(sql)
        values = cursor.fetchall()
        fields = [desc[0] for desc in cursor.description]
    args = map(lambda v: dict(zip(fields, v)), values)
    return list(map(lambda x: klass(**x), args))

def fill(conn):
    insert(conn, list(gen_tags()))
    tags = select_all(conn, Tag)

    insert(conn, list(gen_publishers(30)))
    publishers = select_all(conn, Publisher)

    insert(conn, list(gen_users(publishers, 300)))
    users = select_all(conn, User)
    
    insert(conn, list(gen_products(publishers, 200)))
    products = select_all(conn, Product)

    insert(conn, list(gen_purchases(products, users, 5)))
    purchases = select_all(conn, Purchase)
    products = select_all(conn, Product)

    insert(conn, list(gen_assigned_tags(tags, products, 8)))
    insert(conn, list(gen_gifts(purchases, users, len(users)//2)))
    insert(conn, list(gen_reviews(products, users)))
    insert(conn, list(gen_dependencies(products, 4)))
    