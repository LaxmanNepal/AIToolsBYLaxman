import json, html
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import re

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'tools.json'
GO=ROOT/'go'
BASE='https://ai.laxmannepal.com.np'
SOURCE='ai.laxmannepal.com.np'

def slug(s):
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',str(s).lower())).strip('-')

def tracked(url):
    p=urlsplit(url)
    q=dict(parse_qsl(p.query,keep_blank_values=True))
    q.setdefault('utm_source',SOURCE)
    q.setdefault('utm_medium','ai-directory')
    q.setdefault('utm_campaign','ai-tools')
    return urlunsplit((p.scheme,p.netloc,p.path,p.query if False else urlencode(q),p.fragment))

def page(t):
    name=t.get('title') or t.get('name') or 'AI Tool'
    target=tracked(t.get('url') or '#')
    safe=html.escape(target,quote=True)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url={safe}"><title>Opening {html.escape(name)}…</title><script>location.replace({json.dumps(target)});</script></head><body><p>Opening <strong>{html.escape(name)}</strong>… <a href="{safe}">Continue</a></p></body></html>'''

def main():
    tools=json.loads(DATA.read_text(encoding='utf-8'))
    GO.mkdir(exist_ok=True)
    for t in tools:
        d=GO/slug(t.get('title') or t.get('name') or 'ai-tool')
        d.mkdir(parents=True,exist_ok=True)
        (d/'index.html').write_text(page(t),encoding='utf-8')
    # Rewrite the generated detail-page CTA to use the short redirect URL.
    for t in tools:
        s=slug(t.get('title') or t.get('name') or 'ai-tool')
        f=ROOT/'tools'/s/'index.html'
        if not f.exists(): continue
        text=f.read_text(encoding='utf-8')
        target=t.get('url') or '#'
        pattern=r'(<a class="primary" href=")[^"]*("[^>]*>Visit )'
        text,n=re.subn(pattern,rf'\g<1>{BASE}/go/{s}/\g<2>',text,count=1)
        f.write_text(text,encoding='utf-8')
    print(f'Generated {len(tools)} tracked redirect links under /go/.')

if __name__=='__main__': main()
