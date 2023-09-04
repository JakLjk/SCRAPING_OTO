from sqlalchemy import text

from ..webhook import db


def fetch_row_from_db():
    sql = text(f"""
    SELECT ID_O_P, Offer_Details, Equipment_Details
    FROM offer_details_parsed
    WHERE NOT (EXISTS (SELECT * 
        FROM separated_details_helper_table
        WHERE offer_details_parsed.`ID_O_P` = separated_details_helper_table.`ID_O_P`))
    LIMIT 1 FOR UPDATE SKIP LOCKED""")
    with db.engine.connect() as conn:
        result = conn.execute(sql)
        result = result.first()
    if result:
        return result.first()
    else:
        raise ValueError("No result returned from db")
    
def get_currently_available_column_names(table_name):
    sql = text(f"""SELECT column_name
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{str(table_name)}'""")
    with db.engine.connect() as conn:
        result = conn.execute(sql)
    if result:
        return [name[0] for name in result.all()]
    else:
        raise ValueError("No result returned from db")

def add_column(table_name, column_name, data_type):
    sql = text(f"""ALTER TABLE {table_name}
    ADD {column_name} {data_type}""")
    with db.engine.connect() as conn:
        conn.execute(sql)
        conn.commit()
 
def insert_data_into_helper_table(table_name, insert_dict):
    col_names_list = list(insert_dict.keys())
    col_values_list = list(insert_dict.values())

    col_names_list = [f"`{name}`" for name in col_names_list]
    columns_parsed = ",".join(col_names_list)
    values_parsed = ",".join([f"\"{val}\"" for val in col_values_list])

    sql = \
    f"""INSERT INTO {table_name} ({columns_parsed}) 
    VALUES ({values_parsed})"""
    with db.engine.connect() as conn:
        print(text(sql))
        conn.execute(text(sql))
        conn.commit()
