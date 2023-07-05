#! /usr/bin/env python3

from textrepo.client import TextRepoClient


translatin_tr_uri = 'https://translatin.tt.di.huc.knaw.nl/textrepo'
TR = TextRepoClient(base_uri=translatin_tr_uri, verbose=True)

types = TR.read_file_types()
print(f"types: {types}")


def register_type(name, mediatype):
    if not next((x for x in types if x.name == name), False):
        TR.create_file_type(name, mediatype)


# https://stackoverflow.com/questions/4212861/what-is-a-correct-mime-type-for-docx-pptx-etc
register_type('doc', 'application/msword')
register_type('docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
register_type('mets', 'application/vnd.mets+xml')
register_type('pagexml', 'application/vnd.prima.page+xml')
register_type('pdf', 'application/pdf')
register_type('transmeta', 'application/vnd.transkribus+xml')
register_type('txt', 'text/plain')

types = TR.read_file_types()
print(f"types: {types}")
