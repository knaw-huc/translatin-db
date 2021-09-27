#!/usr/bin/env python3
import sys
import base64
import zlib

kroki_url = 'https://kroki.io/erd/svg'

source = sys.stdin.read().encode('UTF-8')
base64 = base64.urlsafe_b64encode(zlib.compress(source, 9))
diagram = base64.decode('UTF-8')

print(f'{kroki_url}/{diagram}')
