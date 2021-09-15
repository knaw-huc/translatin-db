#!/usr/bin/env python3

from icecream import ic
from openpyxl import load_workbook

import psycopg2.extras
from psycopg2.extensions import AsIs

import uuid

from mapping import MF_ORIGIN, MF_EARLIEST, MF_LATEST, MF_FINGERPRINT, MF_FORM, MF_FORM_TYPE, \
    MF_GENRE, MF_SUBGENRE, MF_CHARACTERS, MF_REMARKS, MF_LITERATURE

wb = load_workbook("/Users/jong/prj/translatin/download/TransLatin_Manifestations.xlsx")
ic(wb.sheetnames)

sheet = wb['Blad1']
pers = ic(sheet['CH39'].value)
ic(pers.split('_x000B_'))  # vertical tab \u000B encoded


def create_manifestations(cursor):
    # for i in range(1, sheet.max_column + 1):
    #     ic(sheet.cell(row=1, column=i).value)

    for row in sheet.iter_rows(min_row=2, values_only=True):
        man = {
            'origin': row[MF_ORIGIN],
            'earliest': row[MF_EARLIEST],
            'latest': row[MF_LATEST],
            'fingerprint': row[MF_FINGERPRINT],
            'form': row[MF_FORM],
            'form_type': row[MF_FORM_TYPE],
            'genre': row[MF_GENRE],
            'subgenre': row[MF_SUBGENRE],
            'characters': row[MF_CHARACTERS],
            'remarks': row[MF_REMARKS],
            'literature': row[MF_LITERATURE]
        }
        ic(man)
        save_manifestation(cursor, man)


def save_manifestation(cursor, man):
    if 'id' not in man:
        man['id'] = uuid.uuid4()

    stmt = 'INSERT INTO manifestations (%s) VALUES %s'

    columns = man.keys()
    values = [man[column] for column in columns]
    data = (AsIs(','.join(columns)), tuple(values))

    ic(cursor.mogrify(stmt, data))
    cursor.execute(stmt, data)

    count = cursor.rowcount
    ic(count, "Record inserted")


def show_titles():
    for row in sheet.iter_rows(min_row=1, max_row=1, values_only=True):
        for i in range(0, len(row)):
            print(f"col[{i}]={row[i]}")


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
        create_manifestations(curs)
        conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')
