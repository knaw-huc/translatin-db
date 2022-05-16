import hashlib
from icecream import ic


def show_titles(sheet):
    for row in sheet.iter_rows(min_row=1, max_row=1, values_only=True):
        for i in range(0, len(row)):
            print(f"col[{i}]={row[i]}")


def fix_duplicates(origin, original):
    normalised = list(dict.fromkeys(original))  # as of Python 3.7 also maintains original insertion order
    if normalised != original:
        ic('FIXING DUPLICATE: ', origin, original)
    return normalised


def sha224sum(filename):
    h  = hashlib.sha224()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n:= f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()
