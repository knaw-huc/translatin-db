#!/usr/bin/env python3

from icecream import ic
from openpyxl import load_workbook

import psycopg2.extras
from psycopg2.extensions import AsIs
from psycopg2.extras import execute_values

import uuid

wb = load_workbook("/Users/jong/prj/translatin/download/TransLatin_Authors.xlsx")
ic(wb.sheetnames)
sheet = wb['Authors']


def show_titles():
    for row in sheet.iter_rows(min_row=1, max_row=1, values_only=True):
        for i in range(0, len(row)):
            print(f"col[{i}]={row[i]}")


show_titles()
