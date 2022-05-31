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


def create_expression(cursor, label):
    expression_id = uuid.uuid4()
    stmt = 'INSERT INTO expressions (id, label) VALUES (%s, %s)'
    data = (expression_id, label)
    cursor.execute(stmt, data)
    return expression_id


def find_similar_manifestations(cursor):
    stmt = open(path, 'r').read()
    cursor.execute(stmt)
    rows = cursor.fetchall()
    eid = 0
    for row in rows:
        eid += 1
        expression_id = create_expression(cursor, f'E{eid}')
        mids = [id for id in row if id is not None]
        for mid in mids:
            stmt = 'INSERT INTO expression_manifestations (expression_id, manifestation_id) ' \
                   'VALUES (%s, (SELECT id FROM manifestations WHERE origin = %s))'
            data = (expression_id, mid)
            cursor.execute(stmt, data)


conn = None
try:
    print('Connecting to translatin database...')
    psycopg2.extras.register_uuid()
    conn = psycopg2.connect(**parser['db'])
    with conn.cursor() as curs:
        find_similar_manifestations(curs)
        conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed')
