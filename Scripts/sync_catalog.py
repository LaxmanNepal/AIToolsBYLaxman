import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'tools.json'
SOURCES = [
    ('AIFOXX', 'https://raw.githubusercontent.com/withkarann/aifoxx/main/src/data/tools.json'),
    ('AI_TOOLS_DATABASE', 'https://raw.githubusercontent.com/Durgesh-Vaigandla/AI-tools-database/main/data/tools.json'),
    ('FREE_AI', 'https://raw.githubusercontent.com/chid/free-ai/main/README.md'),
]

AI_WORDS = ('ai', 'llm', 'model', 'machine learning', 'ml', 'agent', 'vision', 'language', 'image', 'audio', 'video', 'nlp', 'automation', 'generative')
FREE_WORDS = ('unlimited free', '100% free', '100% forever free', 'free forever', 'completely free', 'fully free', 'no limits', 'unlimited access', 'unlimited use', 'free and unlimited')
SELF_HOST_WORDS = ('self-host', 'self hosted', 'self-hosted', 'run locally', 'local ai', 'offline ai', 'on-device')

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'LaxmanNepal-AITools-Catalog-Sync/3.0'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode('utf-8')

def slug(name):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', str(name).lower())).strip('-')

def normalize(t, source):
    name = t.get('name') or t.get('title')
    url = t.get('url') or t.get('website') or t.get('homepage') or t.get('link')
    if not name or not url:
        return None
    category = t.get('category') or 'Other AI'
    if isinstance(category, str):
        category = category.replace('_', ' ').replace('-', ' ').title()
    tags = t.get('tags') or []
    if isinstance(tags, str): tags = [tags]
    metadata = t.get('metadata') or {}
    description = t.get('description') or ''
    pricing_raw = t.get('pricing') or t.get('price') or t.get('free_tier') or ''
    github = t.get('github_url') or metadata.get('github_url') or t.get('source_url') or ''
    license_name = str(t.get('license') or metadata.get('license') or '').lower()
    open_source = bool(t.get('open_source') or metadata.get('open_source') or github)
    text = f'{name} {category} {description} {" ".join(map(str, tags))} {pricing_raw}'.lower()
    ai_relevant = any(w in text for w in AI_WORDS)
    explicit_free = any(w in text for w in FREE_WORDS)
    local_ai = any(w in text for w in SELF_HOST_WORDS)
    permissive = any(x in license_name for x in ('mit', 'apache', 'bsd', 'mpl', 'isc', 'gpl', 'agpl', 'lgpl', 'cc-by'))
    unlimited = ai_relevant and (local_ai or (open_source and permissive) or explicit_free)
    pricing = pricing_raw or ('Unlimited Free' if unlimited else 'Pricing not publicly verified')
    return {
        'title': name,
        'description': description or f'{name} — AI tool.',
        'url': url,
        'logo': t.get('logo') or f"{url.rstrip('/')}/favicon.ico",
        'pricing': 'Unlimited Free' if unlimited else pricing,
        'category': 'Unlimited Free AI Tools' if unlimited else category,
        'original_category': category,
        'tags': tags,
        'last_verified': t.get('last_verified') or t.get('lastUpdated'),
        'access_methods': t.get('access_methods') or [],
        'self_hostable': bool(local_ai or (open_source and permissive)),
        'open_source': open_source,
        'license': t.get('license') or metadata.get('license'),
        'github_url': github,
        'pricing_verified': bool(pricing_raw),
        'unlimited_free_verified': bool(unlimited),
        'source': source,
    }

def parse_free_ai(markdown):
    # Convert bullet entries such as: * Tool - description / limitation
    out=[]
    for line in markdown.splitlines():
        m=re.match(r'^\s*[-*]\s+\*?\*?([^–—-]{2,80})\*?\*?\s*[-–—:]\s+(.+)$', line)
        if not m: continue
        name=m.group(1).strip(' *`')
        rest=m.group(2).strip()
        if not any(w in (name+' '+rest).lower() for w in AI_WORDS): continue
        # Markdown directory entries frequently contain a URL in the text.
        u=re.search(r'https?://[^\s)]+', rest)
        if not u: continue
        out.append({'name':name,'description':rest,'category':'Free AI Tools','url':u.group(0).rstrip('.,') ,'pricing':'Free'})
    return out

def main():
    local=json.loads(DATA.read_text(encoding='utf-8'))
    merged=[]; seen=set()
    for raw in local:
        t=raw if raw.get('title') else normalize(raw,'local')
        if t:
            key=str(t.get('url') or '').rstrip('/').lower() or slug(t.get('title'))
            if key not in seen: seen.add(key); merged.append(t)
    for source,url in SOURCES:
        try:
            raw=fetch(url)
            if url.endswith('.md'):
                external=parse_free_ai(raw)
            else:
                external=json.loads(raw)
                if isinstance(external,dict): external=external.get('tools') or external.get('data') or []
            added=0
            for item in external:
                t=normalize(item,source)
                if not t: continue
                key=str(t.get('url') or '').rstrip('/').lower() or slug(t.get('title'))
                if key not in seen: seen.add(key); merged.append(t); added+=1
            print(f'{source}: imported {added}')
        except Exception as e:
            print(f'{source}: warning: {e}')
    # Prefer confirmed unlimited-free tools first, then alphabetical.
    merged.sort(key=lambda x:(x.get('category')!='Unlimited Free AI Tools', str(x.get('title','')).lower()))
    DATA.write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    unlimited=sum(x.get('category')=='Unlimited Free AI Tools' for x in merged)
    print(f'Catalog ready: {len(merged)} unique tools; {unlimited} unlimited-free candidates.')
    if len(merged)<5000: raise SystemExit(f'Need 5000+ tools; found {len(merged)}')
    if unlimited<100: raise SystemExit(f'Need 100+ confirmed unlimited-free tools; found {unlimited}')

if __name__=='__main__': main()
