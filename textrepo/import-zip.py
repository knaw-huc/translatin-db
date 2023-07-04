#! /usr/bin/env python3

import datetime
import re
import sys
import time
import zipfile

from textrepo.client import TextRepoClient

# Manifestation ID marker in filename
RE_MF_ID_IN_FILENAME = re.compile('M[0-9]+,')

translatin_tr_uri = 'https://translatin.tt.di.huc.knaw.nl/textrepo'
TR = TextRepoClient(base_uri=translatin_tr_uri, verbose=False)


def import_file(mid, filename, type, data):
    while True:
        now = datetime.datetime.now()
        now_str = now.strftime('%Y-%m-%dT%H:%M:%S')
        try:
            version = TR.import_version(mid, type, data, True)
            print(f'{now_str}|PASS|{mid}|{type}|{version}')
            TR.set_file_metadata(version.file_id, 'filename', filename)
            break
        except Exception as e:
            print(f"{now_str}|FAIL|{mid}|{type}|{e}")
            time.sleep(5)


def import_pagexml(mid, filename, data):
    seqnr = filename.split('_')[0]
    import_file(mid + '_' + seqnr, filename, 'pagexml', data)


def import_zip(mid, archive):
    for info in archive.infolist():
        item = info.filename.split('/')[-1]
        data = archive.read(info.filename)
        if item.endswith('.doc'):
            import_file(mid, item, 'doc', data)
        elif item.endswith('.docx'):
            import_file(mid, item, 'docx', data)
        elif item.endswith('.pdf'):
            import_file(mid, item, 'pdf', data)
        elif item.endswith('.xml'):
            if item.endswith('metadata.xml'):
                import_file(mid, item, 'transmeta', data)
            elif item.endswith('mets.xml'):
                import_file(mid, item, 'mets', data)
            else:
                import_pagexml(mid, item, data)
        else:
            now = datetime.datetime.now()
            now_str = now.strftime('%Y-%m-%dT%H:%M:%S')
            print(f'{now_str}|SKIP|{info.filename}')


if __name__ == '__main__':
    prg = sys.argv[0]
    if len(sys.argv) < 2:
        print(f'Usage: {prg} <zipfile>')
        sys.exit(1)

    zip_name = sys.argv[1]
    if not zipfile.is_zipfile(zip_name):
        print(f'{prg}: {zip_name} is not a zip file')
        sys.exit(1)

    filename = zip_name.split('/')[-1]
    if not RE_MF_ID_IN_FILENAME.match(filename):
        print(f'{filename}: does not start with "Mxxxx," marker')
        sys.exit(1)

    mid = filename.split(',')[0]
    print(f'Manifestation ID: {mid}')

    try:
        with zipfile.ZipFile(zip_name, 'r') as archive:
            import_zip(mid, archive)
    except zipfile.BadZipFile as error:
        print(f'Error in {zip_name}: {error}')
