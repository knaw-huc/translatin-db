#!/usr/bin/env python3

import configparser
import os
import uuid

import psycopg2.extras
from icecream import ic
from psycopg2.extras import execute_values

parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
parser.read('config.ini')
conf = parser('base')
path = ic(conf['work'])


def find_similar_expressions(cursor, find_similar_expressions_query):
    # send the query to the database
    print('Computing expression classes')
    cursor.execute(find_similar_expressions_query)

    # read all the result rows
    rows = cursor.fetchall()
    print(f'Found {len(rows)} (compound) Works')

    # keep a running serial number for all Works: "W1", "W2", …
    serialno = 1

    # go over all rows, each row is one of the equivalence classes:
    #   row[0] = {E69, E72}
    #   row[1] = {E78, E630}
    #   …
    # We will assign new Work labels to each equivalence class:
    #   W1 = {E69, E72}
    #   W2 = {E78, E630}
    #   W3 = {…}
    #   …
    for row in rows:
        # translate serial number to label: 1 -> "W1", 2 -> "W2", …
        work_label = f'W{serialno}'

        # and update serial number for next iteration
        serialno += 1

        # create a new Work: W1, W2, … and remember its UUID
        work_id = create_work(cursor, work_label)

        # extract all Expression lables (E69, E72, …) that are in this row / Work
        expr_labels = [id for id in row if id is not None]
        print(f'{work_label}: {expr_labels}')

        # link each expression label to the Work
        for el in expr_labels:
            link_expression_to_work(cursor, el, work_id)

        return serialno


def create_work(cursor, label):
    # label = e.g. "W12"
    # work_id = UUID
    work_id = uuid.uuid4()
    stmt = 'INSERT INTO works (id, label) VALUES (%s, %s)'
    data = (work_id, label)
    cursor.execute(stmt, data)
    return work_id


def link_expression_to_work(cursor, expr_label, work_id):
    # expr_label = e.g. "E69"
    # work_id = UUID
    stmt = 'INSERT INTO work_expressions (work_id, expression_id) ' \
            ' VALUES (%s, (SELECT id FROM expressions WHERE label = %s))'
    data = (work_id, expr_label)
    cursor.execute(stmt, data)


def assign_leftover_expressions(cursor, first_free_serial):
    find_leftover_expressions_query='''
    SELECT e.label
    FROM expressions e
    WHERE NOT EXISTS (
        SELECT FROM work_expressions we WHERE we.expression_id = e.id
    )
    ORDER BY (SUBSTRING(e.label, 2, LENGTH(e.label)-1))::int
    '''

    print('FInding leftover expressions')
    cursor.execute(find_leftover_expressions_query)

    rows = cursor.fetchall()
    print(f'Found {len(rows)} leftover Expressions')

    serialno = first_free_serial
    for expr_label in rows:
        work_label = f'W{serialno}'
        print(f'{work_label}: {expr_label}')
        serialno += 1
        work_id = create_work(cursor, work_label)
        link_expression_to_work(cursor, expr_label, work_id)


conn = None
try:
    print(f'Reading query from {path}:')
    stmt = open(path, 'r').read()
    print(stmt)


    print('Connecting to translatin database')
    psycopg2.extras.register_uuid()
    conn = psycopg2.connect(**parser['db'])
    with conn.cursor() as curs:
        print('Collecting similar expressions into works')
        serial = find_similar_expressions(cur, stmt)
        print('Assigning leftover expressions to singleton works')
        assign_leftover_expressions(curs, serial)
        print('Committing results')
        conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed')
