from typing import List, Tuple
from .data import *
from .gen import *
from matplotlib import pyplot as plt

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

def move_1_gift_to_direct_purchase(connection):
    find_gift_sql = f"SELECT id, purchase_id, recipient_id FROM {Gift.table_name} LIMIT 1"
    with connection, connection.cursor() as cursor:
        cursor.execute(find_gift_sql)
        values = cursor.fetchone()
        gift_id = values[0]
        purchase_id = values[1]
        user_id = values[2]
    delete_gift_sql = f"DELETE FROM {Gift.table_name} WHERE id={gift_id}"
    update_purcahse_sql = f"UPDATE {Purchase.table_name} SET buyer_id={user_id} WHERE id={purchase_id}"
    with connection, connection.cursor() as cursor:
        cursor.execute(delete_gift_sql)
        cursor.execute(update_purcahse_sql)
    



def measure_execution_time(connection, query: str) -> float:
    measure_query = f"EXPLAIN ANALYZE {query}"
    with connection, connection.cursor() as cursor:
        cursor.execute(measure_query)
        fetch = cursor.fetchall()
    string = list(filter(lambda x: x[0].startswith('Execution Time:'), fetch))[0][0]
    time_ms_str = string.removeprefix('Execution Time: ').removesuffix(' ms')
    return float(time_ms_str)


def graph(conn):
    purchases = 10**5
    initial_fill(conn, purchases)
    sql = """
    WITH library_purchases AS (
    SELECT g.purchase_id
        FROM Gift AS g
        WHERE recipient_id = 1
    UNION ALL
    SELECT pur.id AS purchase_id
        FROM (SELECT * FROM Purchase AS pur WHERE pur.buyer_id = 1) AS pur
        LEFT JOIN Gift AS g
        ON pur.id = g.purchase_id
        WHERE g.purchase_id IS NULL
    )
    SELECT DISTINCT ON (prod.id) prod.*, pur.date
        FROM library_purchases AS lib_pur
        INNER JOIN Purchase AS pur
        ON lib_pur.purchase_id = pur.id
        INNER JOIN Product AS prod
        ON pur.product_id = prod.id;
    """
    timing = []
    for _ in range(purchases):
        timing.append(measure_execution_time(conn, sql))
        move_1_gift_to_direct_purchase(conn)

    with open('measure_insert', 'w') as file:
        file.write(str(timing))
    plt.plot(list(range(purchases)), timing, label='get lib')
    plt.legend()
    plt.show()



def initial_fill(conn, purchases: PositiveInt):
    insert(conn, list(gen_publishers(1)))
    publisher = select_all(conn, Publisher)[0]
    
    insert(conn, list(gen_2_users()))
    user1, user2  = select_all(conn, User)
    
    insert(conn, list(gen_products([publisher], purchases)))
    products = select_all(conn, Product)
    
    
    insert(conn, list(gen_purchases(products, user2)))
    purchases = select_all(conn, Purchase)
    
    insert(conn, list(gen_all_gifts(purchases, user1)))
