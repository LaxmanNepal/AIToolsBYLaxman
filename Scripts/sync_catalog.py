import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'tools.json'
SOURCES = [
    ('AIFOXX', 'https://raw.githubusercontent.com/withkarann/aifoxx/main/src/data/tools.json'),
    ('SKOPX', 'https://raw.githubusercontent.com/skopx/AI-tools/main/tools.json'),
]

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'LaxmanNepal-AITools-Catalog-Sync/2.0'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode('utf-8'))

def slug(name):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', str(name).lower())).strip('-')

def normalize(t, source):
    name = t.get('name') or t.get('title')
    url = t.get('url') or t.get('website') or t.get('homepage')
    if not name or not url:
        return None
    category = t.get('category') or 'Other AI'
    if isinstance(category, str):
        category = category.replace('_', ' ').replace('-', ' ').title()
    tags = t.get('tags') or []
    if isinstance(tags, str):
        tags = [tags]
    metadata = t.get('metadata') or {}
    github = t.get('github_url') or metadata.get('github_url') or t.get('source_url')
    license_name = str(t.get('license') or metadata.get('license') or '').lower()
    open_source = bool(t.get('open_source') or metadata.get('open_source') or github) and bool(github)
    # Unlimited Free means software that can be downloaded/self-hosted locally.
    # Do not label hosted free tiers as unlimited.
    ai_words = ('ai', 'llm', 'model', 'machine learning', 'ml', 'agent', 'vision', 'language', 'image', 'audio', 'video', 'nlp', 'automation')
    text = f'{name} {category} {t.get("description", "")} {" ".join(map(str, tags))}'.lower()
    ai_relevant = any(w in text for w in ai_words)
    permissive = any(x in license_name for x in ('mit', 'apache', 'bsd', 'mpl', 'isc', 'gpl', 'agpl', 'lgpl', 'cc-by')) or open_source
    unlimited = open_source and permissive and ai_relevant
    pricing = t.get('pricing') or t.get('price') or ('Open Source' if unlimited else 'Check provider')
    return {
        'title': name,
        'description': t.get('description') or f'{name} — AI tool.',
        'url': url,
        'logo': t.get('logo') or f"{url.rstrip('/')}/favicon.ico",
        'pricing': 'Unlimited Free' if unlimited else pricing,
        'category': 'Unlimited Free AI Tools' if unlimited else category,
        'original_category': category,
        'tags': tags,
        'last_verified': t.get('last_verified'),
        'access_methods': t.get('access_methods') or [],
        'self_hostable': unlimited,
        'open_source': open_source,
        'license': t.get('license') or metadata.get('license'),
        'github_url': github,
        'source': source,
    }

def main():
    local = json.loads(DATA.read_text(encoding='utf-8'))
    merged = []
    seen = set()
    for raw in local:
        t = raw if raw.get('title') else normalize(raw, 'local')
        if t:
            key = str(t.get('url') or '').rstrip('/').lower() or slug(t.get('title'))
            if key not in seen:
                seen.add(key); merged.append(t)
    for source, url in SOURCES:
        try:
            external = fetch(url)
            if isinstance(external, dict):
                external = external.get('tools') or external.get('data') or []
            for raw in external:
                t = normalize(raw, source)
                if not t:
                    continue
                key = str(t.get('url') or '').rstrip('/').lower() or slug(t.get('title'))
                if key not in seen:
                    seen.add(key); merged.append(t)
            print(f'{source}: imported')
        except Exception as e:
            print(f'{source}: warning: {e}')
    merged.sort(key=lambda x: (x.get('category') != 'Unlimited Free AI Tools', str(x.get('title', '')).lower()))
    DATA.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    unlimited = sum(x.get('category') == 'Unlimited Free AI Tools' for x in merged)
    print(f'Catalog ready: {len(merged)} unique tools; {unlimited} unlimited-free candidates.')
    if len(merged) < 5000:
        raise SystemExit(f'Catalog expansion failed: only {len(merged)} tools available; need 5000+')
    if unlimited < 100:
        raise SystemExit(f'Unlimited-free expansion failed: only {unlimited} candidates; need 100+')

if __name__ == '__main__':
    main()
