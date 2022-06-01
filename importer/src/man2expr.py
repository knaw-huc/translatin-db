#!/usr/bin/env python3

import configparser
import os
import uuid

import psycopg2.extras
from icecream import ic
from psycopg2.extras import execute_values

parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
parser.read('config.ini')
conf = parser['base']
path = ic(conf['expr'])


def find_similar_manifestations(cursor, find_similar_manifestations_query):
    # send the query to the database
    print('Computing manifestation equivalence classes')
    cursor.execute(find_similar_manifestations_query)

    # read all the result rows
    rows = cursor.fetchall()
    print(f'Found {len(rows)} Expressions')

    # keep a running serial number for all Expressions: "E1", "E2", …
    serialno = 1

    # go over all rows, each row is one of the equivalence classes:
    #   row[0] = {M1, M3, M6}
    #   row[1] = {M2, M9, M10, …}
    #   row[2] = {…}
    #   …
    # We will assign new Expression labels to each equivalence class:
    #   E1 = {M1, M3, M6}
    #   E2 = {M2, M9, M10, …}
    #   E3 = {…}
    #   …
    for row in rows:
        # translate serial number to label: 1 -> "E1", 2 -> "E2", …
        expression_label = f'E{serialno}'

        # and update serial number for next iteration
        serialno += 1

        # create a new Expression: E1, E2, … and remember its UUID
        expression_id = create_expression(cursor, expression_label)

        # extract all Manifestation origins (M1, M3, …) that are in this row / Expression
        origins = [id for id in row if id is not None]
        print(f'{expression_label}: {origins}')

        # link each origin to the Expression
        for origin in origins:
            link_manifestation_to_expression(cursor, origin, expression_id)


def create_expression(cursor, label):
    # label = e.g. "E12"
    # expression_id = UUID
    expression_id = uuid.uuid4()
    stmt = 'INSERT INTO expressions (id, label) VALUES (%s, %s)'
    data = (expression_id, label)
    cursor.execute(stmt, data)
    return expression_id


def link_manifestation_to_expression(cursor, manifestation_origin, expression_id):
    # manifestation_origin = e.g. 'M123'
    # expression_id = UUID
    stmt = 'INSERT INTO expression_manifestations (expression_id, manifestation_id) ' \
           'VALUES (%s, (SELECT id FROM manifestations WHERE origin = %s))'
    data = (expression_id, manifestation_origin)
    cursor.execute(stmt, data)


conn = None
try:
    print(f'Reading query from {path}:')
    stmt = open(path, 'r').read()
    print(stmt)

    print('Connecting to translatin database')
    psycopg2.extras.register_uuid()
    conn = psycopg2.connect(**parser['db'])
    with conn.cursor() as curs:
        find_similar_manifestations(curs, stmt)
        print('Committing results')
        conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed')
