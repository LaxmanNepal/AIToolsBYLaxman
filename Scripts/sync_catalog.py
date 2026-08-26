import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'tools.json'
SOURCE = 'https://raw.githubusercontent.com/withkarann/aifoxx/main/src/data/tools.json'

# AIFOXX is an open-source directory with a public machine-readable catalog.
# We merge it with the local catalog rather than replacing local entries.
def fetch_source():
    req = urllib.request.Request(SOURCE, headers={'User-Agent': 'LaxmanNepal-AITools-Catalog-Sync/1.0'})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode('utf-8'))

def slug(name):
    import re
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', str(name).lower())).strip('-')

def normalize(t):
    name = t.get('name') or t.get('title')
    if not name or not t.get('url'):
        return None
    pricing = t.get('pricing') or t.get('price') or 'Check provider'
    category = t.get('category') or 'Other AI'
    self_hostable = (t.get('data_storage') or {}).get('self_hostable')
    tags = t.get('tags') or []
    # Only classify confirmed self-hostable software as unlimited-free.
    # Open-source alone is not enough because a hosted service can still impose limits.
    unlimited = self_hostable is True
    return {
        'title': name,
        'description': t.get('description') or f'{name} — AI tool.',
        'url': t.get('url'),
        'logo': t.get('logo') or f"{t.get('url').rstrip('/')}/favicon.ico",
        'pricing': 'Unlimited Free' if unlimited else pricing,
        'category': 'Unlimited Free AI Tools' if unlimited else category,
        'original_category': category,
        'tags': tags,
        'last_verified': t.get('last_verified'),
        'access_methods': t.get('access_methods') or [],
        'self_hostable': self_hostable,
        'source': 'AIFOXX'
    }

def main():
    local = json.loads(DATA.read_text(encoding='utf-8'))
    try:
        external = fetch_source()
    except Exception as e:
        print(f'Catalog sync warning: {e}')
        external = []

    merged = []
    seen = set()
    for raw in local + [normalize(x) for x in external]:
        if raw is None:
            continue
        t = raw if 'title' in raw else normalize(raw)
        if not t:
            continue
        key = str(t.get('url') or '').rstrip('/').lower() or slug(t.get('title'))
        if key in seen:
            continue
        seen.add(key)
        merged.append(t)

    merged.sort(key=lambda x: (x.get('category') != 'Unlimited Free AI Tools', str(x.get('title','')).lower()))
    DATA.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    unlimited = sum(x.get('category') == 'Unlimited Free AI Tools' for x in merged)
    print(f'Catalog ready: {len(merged)} unique tools; {unlimited} unlimited-free/self-hosted candidates.')
    if len(merged) < 1000:
        raise SystemExit(f'Catalog expansion failed: only {len(merged)} tools available')
    if unlimited < 1:
        raise SystemExit('No confirmed self-hosted tools available for Unlimited Free AI Tools')

if __name__ == '__main__':
    main()
