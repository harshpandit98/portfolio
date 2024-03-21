import json
import sqlite3


def load_json_file(fn):
    with open(fn, "r") as file:
        return json.load(file)


def put_to_db(filename):
    db_name = "temp.db"
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    create_tab_q = """
        CREATE TABLE if not exists 
        listings(
            listing_id integer primary key autoincrement, 
            name text, 
            brand text, 
            price real, 
            image_url text, 
            product_url text
        )
    """
    cur.execute(create_tab_q)

    json_data = load_json_file(filename) or []
    records = []
    for row in json_data:
        records.append(tuple(row.values()))

    insert_q = """
        insert into listings(name, brand, price, image_url, product_url)
        values (?, ?, ?, ?, ?)
    """
    cur.executemany(insert_q, records)
    con.commit()
    print(f"Commited data to db: {db_name}")
