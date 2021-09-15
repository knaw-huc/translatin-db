#!/usr/bin/env python3

from icecream import ic
from openpyxl import load_workbook

import psycopg2.extras
from psycopg2.extensions import AsIs

import uuid


wb = load_workbook("/Users/jong/prj/translatin/download/TransLatin_Manifestations.xlsx")
ic(wb.sheetnames)

it = wb['Blad1']
pers = ic(it['CH39'].value)
ic(pers.split('_x000B_'))  # vertical tab \u000B encoded


def save_manifestation(curs, man):
    columns = man.keys()
    values = [man[column] for column in columns]
    stmt = 'INSERT INTO manifestations (%s) VALUES %s'
    data = (AsIs(','.join(columns)), tuple(values))
    ic(curs.mogrify(stmt, data))
    curs.execute(stmt, data)
    conn.commit()
    count = curs.rowcount
    ic(count, "Record inserted")
    return curs.fetchone()


def mock():
    record = {}
    record['id'] = uuid.uuid4()
    record['earliest'] = '1511-01-01'
    record['latest'] = '1511-12-31'
    record['form'] = None
    record['form_type'] = 'Full edition'
    record['genre'] = ''
    # return {'earliest': '1511-01-01', 'form_type': 'Full edition', 'latest': '1511-12-31', 'id': uuid.uuid4()}
    return record


conn = None
try:
    print("Connecting to translatin database...")
    psycopg2.extras.register_uuid()
    conn = psycopg2.connect(host="localhost",
                            database="translatin",
                            user="translatin",
                            password="translatin")
    with conn.cursor() as curs:
        curs.execute("select version()")
        version = curs.fetchone()
        ic(version)
        ic(save_manifestation(curs, mock()))
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')
