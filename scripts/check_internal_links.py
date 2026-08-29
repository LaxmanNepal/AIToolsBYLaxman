#!/usr/bin/env python3
"""Check relative HTML links and asset references in the generated site."""
from __future__ import annotations
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
ROOT=Path(__file__).resolve().parents[1]
SKIP_EXT={'.json','.xml'}
PATTERN=re.compile(r'''(?:href|src)=["']([^"'#]+)["']''',re.I)
def main():
    errors=[]; files=list(ROOT.rglob('*.html'))
    for page in files:
        text=page.read_text(encoding='utf-8',errors='ignore')
        for ref in PATTERN.findall(text):
            if ref.startswith(('http://','https://','mailto:','tel:','data:','javascript:')): continue
            target=unquote(ref.split('?')[0])
            p=(page.parent/target).resolve()
            try: p.relative_to(ROOT.resolve())
            except ValueError: errors.append(f'{page}: escapes repository: {ref}'); continue
            if target.endswith('/'):
                p=p/'index.html'
            elif p.suffix=='' and p.name:
                p=p.with_suffix('.html')
            if not p.exists() and p.suffix not in SKIP_EXT:
                errors.append(f'{page}: missing {ref}')
    if errors:
        print('\n'.join(errors[:100])); raise SystemExit(f'{len(errors)} internal references failed')
    print(f'Checked {len(files)} generated HTML files: all local references resolve')
if __name__=='__main__': main()
