#!/usr/bin/env python3

from collections import defaultdict
import csv
import mapping
from pathlib import Path

csv_dir = Path('/Users/jong/prj/translatin/archives/Translatin/export_csv')
path = csv_dir / 'Spektakels.csv'


with path.open(newline='') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=mapping.columns)
    found = defaultdict(int)
    distinct = defaultdict(set)
    stats = defaultdict(lambda: defaultdict(int))
    for row in reader:
        for col in mapping.columns:
            val = row[col]
            distinct[col].add(val)
            stats[col][val] += 1
            if val.strip() != "":
                found[col] += 1
#                print(f'[{row[col]}] -> found[{col}] is {found[col]}')

#empty = [col for col in mapping.columns if found[col] == 0]
#print(empty)
#
#print('\n==========[ SINGLES ]===========')
singles = [col for col in mapping.columns if len(distinct[col]) == 1]
#for s in singles:
#    print(f'{s} only has value: [{next(iter(distinct[s]))}]')
#
#print('\n==========[ DOUBLES ]===========')
#doubles = [col for col in mapping.columns if len(distinct[col]) == 2]
#for d in doubles:
#    print(f'{d} only has two values: {distinct[d]}')


interesting = set(mapping.columns) - set(singles)
#print(f'len(interesting)={len(interesting)}')


for col in sorted(interesting):
    by_freq_desc = sorted(stats[col].items(), key = lambda it: (it[1],it[0]), reverse=True)
    highest_freq_tuple = by_freq_desc[0]
    (data, freq) = highest_freq_tuple
    if freq < 4495-100:
        items = ','.join(f'"[{k}] x {v}"' for k,v in by_freq_desc)
        print(f'"{col}",{items}')
