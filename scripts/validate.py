#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=('title','slug','url','category','pricing','description','lastVerified','verificationStatus','verificationConfidence','lifecycleStatus','platforms','languages')

def load_catalog(path):
    payload=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(payload,list):
        return payload
    if isinstance(payload,dict) and isinstance(payload.get('tools'),list):
        return payload['tools']
    raise AssertionError('data/tools.json must contain a tools array')

def main():
    data=ROOT/'data/tools.json'; index=ROOT/'tools/index.json'
    assert data.is_file() and data.stat().st_size>0,'data/tools.json missing'
    assert index.is_file() and index.stat().st_size>0,'tools/index.json missing'
    tools=load_catalog(data); compact=json.loads(index.read_text(encoding='utf-8'))
    assert isinstance(compact,list), 'tools/index.json must be an array'
    assert len(tools)>=500,f'Expected 500+ tools, found {len(tools)}'
    assert len(compact)==len(tools),'Discovery index count mismatch'
    assert len(index.read_bytes())<len(data.read_bytes()),'Discovery index is not smaller than canonical data'
    slugs=set(); urls=set(); cats=set()
    for t in tools:
        missing=[k for k in REQUIRED if not t.get(k)]
        assert not missing,f'Missing fields {missing} for {t.get("title")}'
        title,url,slug=str(t['title']).strip(),str(t['url']).strip(),str(t['slug']).strip()
        parsed=urlparse(url)
        assert parsed.scheme in {'http','https'} and parsed.netloc,f'Invalid URL for {title}'
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug),f'Invalid slug: {slug}'
        assert slug not in slugs,f'Duplicate slug: {slug}'
        assert url.rstrip('/').lower() not in urls,f'Duplicate URL: {url}'
        assert len(str(t['description']))<=500,f'Description too long: {title}'
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(t['lastVerified'])),f'Invalid lastVerified: {title}'
        assert t['verificationStatus'] in {'verified','unverified','needs-review'}
        assert t['verificationConfidence'] in {'high','medium','low'}
        assert t['lifecycleStatus'] in {'active','acquired','deprecated','shutdown','needs-review'}
        assert isinstance(t['platforms'],list) and isinstance(t['languages'],list)
        cats.add(t['category']); slugs.add(slug); urls.add(url.rstrip('/').lower())
        assert (ROOT/'tools'/slug/'index.html').is_file(),f'Missing detail page: {slug}'
        assert (ROOT/'go'/slug/'index.html').is_file(),f'Missing redirect: {slug}'
    assert (ROOT/'sitemap.xml').is_file(),'sitemap.xml missing'
    assert (ROOT/'robots.txt').is_file(),'robots.txt missing'
    assert not (ROOT/'AItools').exists(),'Legacy AItools directory remains'
    home=(ROOT/'index.html').read_text(encoding='utf-8')
    js=(ROOT/'assets/js/home.js').read_text(encoding='utf-8')
    assert 'AItools/' not in home,'Legacy AItools route remains in homepage'
    assert 'data/tools.json' in home,'Homepage must document canonical data/tools.json source'
    assert "const DATA_URL = 'data/tools.json'" in js,'Homepage JS must load canonical data/tools.json'
    assert 'tools/index.json' not in js,'Homepage JS must not load discovery index'
    assert 'OPENAI_API_KEY' not in home and 'api.openai.com' not in home,'Secret/API architecture leaked into frontend'
    assert 'OPENAI_API_KEY' not in js and 'api.openai.com' not in js,'Secret/API architecture leaked into homepage JS'
    assert not (ROOT/'everything.json').exists(),'Duplicate everything.json remains'
    assert not (ROOT/'ToolList.txt').exists(),'Obsolete ToolList.txt remains'
    print(f'Validated {len(tools)} tools, {len(cats)} categories, {len(slugs)} routes and {len(urls)} unique URLs')

if __name__=='__main__': main()
