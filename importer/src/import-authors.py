#!/usr/bin/env python3

from icecream import ic
from openpyxl import load_workbook

import psycopg2.extras
from psycopg2.extensions import AsIs
from psycopg2.extras import execute_values

import uuid

from mapping.authors import AUTHOR_BIRTH_PLACE, AUTHOR_DEATH_PLACE

wb = load_workbook("/Users/jong/prj/translatin/download/TransLatin_Authors.xlsx")
ic(wb.sheetnames)
sheet = wb['Authors']


def show_titles():
    for row in sheet.iter_rows(min_row=1, max_row=1, values_only=True):
        for i in range(0, len(row)):
            print(f"col[{i}]={row[i]}")


def collect_places(cursor):
    places = set()
    for row in sheet.iter_rows(min_row=2, values_only=True):    # skip title row
        if row[AUTHOR_BIRTH_PLACE]:
            places.add(row[AUTHOR_BIRTH_PLACE])
        if row[AUTHOR_DEATH_PLACE]:
            places.add(row[AUTHOR_DEATH_PLACE])
    ic(places)

    stmt = "INSERT INTO places (name) VALUES %s"
    data = [(place,) for place in places]
    execute_values(cursor, stmt, data)


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
        # save_manifestation(curs, mock())
        collect_places(curs)
        conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')
