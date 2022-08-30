#!/usr/local/bin/python3

import csv

digraph_pre = '''
digraph wemi {
fontname="Helvetica,Arial,sans-serif"
node [fontname="Helvetica,Arial,sans-serif"]
edge [fontname="Helvetica,Arial,sans-serif"]
rankdir="LR"
node [fontsize=10, shape=box, height=0.25]
edge [fontsize=10]
'''

digraph_suf = '}'


works = dict()

#filename='./work-expr-man-lvstn_20.csv'
filename='./wemi-1.csv'

with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    first = True
    for (w,e,m,t) in reader:
        if first:
            first = False
            continue

        if not w in works:
            works[w] = dict()

        if not e in works[w]:
            works[w][e] = set()

        works[w][e].add((m,t))

def by_label(wl):
    return int(wl[1:])

print(digraph_pre)
for w in sorted(works, key=by_label, reverse=True):
    #    print(f'{w} -> {len(works[w])} -> {works[w]}')
    if len(works[w]) > 1:
        for e in works[w]:
            print(f'\"{w}\" -> \"{e}\"')
            for (m,t) in works[w][e]:
                print(f'\"{m}\" [label=\"{m}\"]')
                print(f'\"{e}\" -> \"{m}\" [label=\"{t}\"]')
    else:
        interesting = False
        for e in works[w]:
            if len(works[w][e]) > 1:
                interesting = True
                break
        if not interesting:
            continue
        for e in works[w]:
            print(f'\"{w}\" -> \"{e}\"')
            for (m,t) in works[w][e]:
                print(f'\"{m}\" [label=\"{m}\"]')
                print(f'\"{e}\" -> \"{m}\" [label=\"{t}\"]')


print(digraph_suf)
