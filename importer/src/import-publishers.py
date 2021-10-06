#!/usr/bin/env python3

import configparser
from icecream import ic
from openpyxl import load_workbook

import psycopg2.extras
from psycopg2.extensions import AsIs
from psycopg2.extras import execute_values

from util import fix_duplicates

import uuid

from mapping.printers import PP_STD_NAME, PP_WED_ERVEN, \
    PP_FIRST_NAME, PP_PATRONYM, PP_PREFIX, PP_SURNAME, PP_ADDITION, \
    PP_ALT_NAMES_FROM, PP_ALT_NAMES_UPTO

parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
parser.read('config.ini')
conf = parser['publishers']
wb = load_workbook(ic(conf['path']))
ic(wb.sheetnames)
sheet = wb[conf['name']]

# show_titles(sheet)

conn = None
unique_names = set()


def create_publishers(cursor):
    for row in sheet.iter_rows(min_row=2, values_only=True):  # skip title row
        name = row[PP_STD_NAME]
        ic(name)

        # avoid postgres zapping us on duplicate names
        if name in unique_names:
            ic('DUPLICATE NAME', name)
            continue
        unique_names.add(name)

        publisher = {
            'name': name,
            'surname': row[PP_SURNAME]
        }

        # Name related data
        if row[PP_WED_ERVEN]:
            publisher['wed_erven'] = row[PP_WED_ERVEN]
        if row[PP_FIRST_NAME]:
            publisher['first_name'] = row[PP_FIRST_NAME]
        if row[PP_PATRONYM]:
            publisher['patronym'] = row[PP_PATRONYM]
        if row[PP_PREFIX]:
            publisher['prefix'] = row[PP_PREFIX]
        if row[PP_ADDITION]:
            publisher['addition'] = row[PP_ADDITION]

        # 1:n relationship with alternative literal names
        names = [row[i] for i in range(PP_ALT_NAMES_FROM, PP_ALT_NAMES_UPTO) if row[i]]
        publisher['_names'] = fix_duplicates(name, names)

        create_publisher(cursor, publisher)


def create_publisher(cursor, publisher):
    if 'id' not in publisher:
        publisher['id'] = uuid.uuid4()

    stmt = 'INSERT INTO publishers (%s) VALUES %s'
    columns = [col for col in publisher.keys() if not col.startswith('_')]
    values = [publisher[col] for col in columns]
    data = (AsIs(','.join(columns)), tuple(values))
    cursor.execute(stmt, data)

    stmt = 'INSERT INTO publisher_names (publisher_id, name) VALUES %s'
    data = [(publisher['id'], name) for name in publisher['_names']]
    execute_values(cursor, stmt, data)

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
        create_publishers(curs)
        conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')
