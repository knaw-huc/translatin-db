#!/usr/local/bin/python3

import csv

digraph_pre = '''
digraph wemi {
fontname="Helvetica,Arial,sans-serif"
node [fontname="Helvetica,Arial,sans-serif"]
edge [fontname="Helvetica,Arial,sans-serif"]
node [fontsize=10, shape=box, height=0.25]
edge [fontsize=10]
'''

digraph_suf = '}'


works = dict()

filename='./auth-publ-3.csv'

print(digraph_pre)

with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    first = True
    for (a,p,c) in reader:
        if first:
            first = False
            continue
        print(f'\"{a}\"')
        print(f'\"{p}\"')
        print(f'\"{a}\" -> \"{p}\" [style=\"filled\" penwidth={int(min(float(c)/8,8))+1} label=\"{c}\"]')

print(digraph_suf)
