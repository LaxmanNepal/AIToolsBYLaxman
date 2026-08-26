import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'tools.json'
SOURCES = [
    ('AIFOXX', 'https://raw.githubusercontent.com/withkarann/aifoxx/main/src/data/tools.json'),
    ('AI_TOOLS_DATABASE', 'https://raw.githubusercontent.com/Durgesh-Vaigandla/AI-tools-database/main/data/tools.json'),
    ('SKOPX_AI_TOOLS', 'https://raw.githubusercontent.com/skopx/AI-tools/main/tools.json'),
    ('FREE_AI', 'https://raw.githubusercontent.com/chid/free-ai/main/README.md'),
]

AI_WORDS = ('artificial intelligence', 'ai ', ' ai', 'llm', 'large language', 'machine learning', 'deep learning', 'generative ai', 'genai', 'agent', 'agentic', 'vision', 'computer vision', 'natural language', 'nlp', 'text to image', 'text-to-image', 'text to video', 'text-to-video', 'image generation', 'speech recognition', 'speech synthesis', 'voice cloning', 'embedding', 'rerank', 'diffusion', 'transformer', 'inference', 'rag', 'retrieval augmented', 'multimodal', 'ocr', 'chatbot', 'copilot', 'automation', 'prompt')
FREE_WORDS = ('unlimited free', '100% free', '100% forever free', 'free forever', 'completely free', 'fully free', 'no limits', 'unlimited access', 'unlimited use', 'free and unlimited')
SELF_HOST_WORDS = ('self-host', 'self hosted', 'self-hosted', 'run locally', 'local ai', 'offline ai', 'on-device', 'on device', 'local inference', 'self deploy', 'self-deploy')
FREE_HOST_WORDS = ('open source', 'open-source', 'free software', 'mit license', 'apache license', 'bsd license', 'gpl license')

# Keep the public catalogue useful rather than importing tens of thousands of unrelated
# GitHub utilities from large ecosystem datasets.  8,000 gives plenty of headroom above
# the requested 5,000 while keeping static-page generation practical.
MAX_TOOLS = 8000


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'LaxmanNepal-AITools-Catalog-Sync/4.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode('utf-8')


def slug(name):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', str(name).lower())).strip('-')


def clean_url(url):
    if not isinstance(url, str):
        return ''
    url = url.strip().strip('`').rstrip('.,;')
    if not url.startswith(('http://', 'https://')):
        return ''
    try:
        p = urlparse(url)
        if not p.netloc:
            return ''
        return url
    except Exception:
        return ''


def normalize(t, source):
    if not isinstance(t, dict):
        return None
    name = t.get('name') or t.get('title') or t.get('product')
    url = clean_url(t.get('url') or t.get('website') or t.get('homepage') or t.get('link'))
    if not name or not url:
        return None

    category = t.get('category') or t.get('category_name') or 'Other AI'
    if isinstance(category, list):
        category = category[0] if category else 'Other AI'
    category = str(category).replace('_', ' ').replace('-', ' ').strip().title()

    tags = t.get('tags') or []
    if isinstance(tags, str):
        tags = [x.strip() for x in re.split(r'[,|]', tags) if x.strip()]
    elif not isinstance(tags, list):
        tags = []

    metadata = t.get('metadata') or {}
    if not isinstance(metadata, dict):
        metadata = {}
    description = str(t.get('description') or t.get('summary') or '').strip()
    pricing_raw = str(t.get('pricing') or t.get('price') or t.get('free_tier') or t.get('pricing_model') or '').strip()
    github = clean_url(t.get('github_url') or metadata.get('github_url') or t.get('source_url') or '')
    license_name = str(t.get('license') or metadata.get('license') or '').lower()

    text = f'{name} {category} {description} {" ".join(map(str, tags))} {pricing_raw}'.lower()
    ai_relevant = any(w in text for w in AI_WORDS)
    explicit_free = any(w in text for w in FREE_WORDS)
    local_ai = any(w in text for w in SELF_HOST_WORDS)
    open_source = bool(t.get('open_source') or metadata.get('open_source') or github)
    permissive = any(x in license_name for x in ('mit', 'apache', 'bsd', 'mpl', 'isc', 'gpl', 'agpl', 'lgpl', 'cc-by'))

    # "Unlimited Free" is intentionally conservative.  A missing price is NOT evidence
    # of free access.  Local/self-hosted open-source software can be used without a
    # vendor-imposed usage meter, but hardware/API costs can still exist.
    unlimited = ai_relevant and (
        explicit_free or
        local_ai or
        (open_source and permissive and any(w in text for w in FREE_HOST_WORDS))
    )

    if unlimited:
        pricing = 'Unlimited Free'
    elif pricing_raw:
        pricing = pricing_raw
    else:
        pricing = 'Pricing not publicly verified'

    return {
        'title': str(name).strip(),
        'description': description or f'{name} — AI tool.',
        'url': url,
        'logo': t.get('logo') or t.get('icon') or f"{url.rstrip('/')}/favicon.ico",
        'pricing': pricing,
        'category': 'Unlimited Free AI Tools' if unlimited else category,
        'original_category': category,
        'tags': tags,
        'last_verified': t.get('last_verified') or t.get('lastUpdated') or t.get('updated_at'),
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
    out = []
    for line in markdown.splitlines():
        m = re.match(r'^\s*[-*]\s+\*?\*?([^–—-]{2,80})\*?\*?\s*[-–—:]\s+(.+)$', line)
        if not m:
            continue
        name = m.group(1).strip(' *`')
        rest = m.group(2).strip()
        if not any(w in (name + ' ' + rest).lower() for w in AI_WORDS):
            continue
        u = re.search(r'https?://[^\s)]+', rest)
        if not u:
            continue
        out.append({'name': name, 'description': rest, 'category': 'Free AI Tools', 'url': u.group(0).rstrip('.,'), 'pricing': 'Free'})
    return out


def main():
    try:
        local = json.loads(DATA.read_text(encoding='utf-8'))
    except Exception:
        local = []

    merged = []
    seen = set()

    def add(item, source):
        t = normalize(item, source)
        if not t:
            return False
        # The homepage uses URL identity, while redirects use slug identity.
        key = t['url'].rstrip('/').lower()
        if key in seen:
            return False
        seen.add(key)
        merged.append(t)
        return True

    for raw in local:
        if raw.get('title') or raw.get('name'):
            add(raw, 'local')

    for source, url in SOURCES:
        try:
            raw = fetch(url)
            if url.endswith('.md'):
                external = parse_free_ai(raw)
            else:
                external = json.loads(raw)
                if isinstance(external, dict):
                    external = external.get('tools') or external.get('data') or external.get('products') or []
            added = 0
            for item in external:
                if add(item, source):
                    added += 1
            print(f'{source}: imported {added}')
        except Exception as e:
            print(f'{source}: warning: {e}')

    # Only keep AI-relevant entries and prefer entries with stronger metadata.
    merged = [x for x in merged if any(w in f"{x['title']} {x['description']} {x['category']} {' '.join(map(str,x['tags']))}".lower() for w in AI_WORDS)]
    merged.sort(key=lambda x: (
        x.get('category') != 'Unlimited Free AI Tools',
        not x.get('pricing_verified', False),
        not x.get('open_source', False),
        str(x.get('title', '')).lower(),
    ))
    merged = merged[:MAX_TOOLS]

    DATA.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    unlimited = sum(x.get('category') == 'Unlimited Free AI Tools' for x in merged)
    unknown_price = sum(not x.get('pricing_verified') for x in merged)
    print(f'Catalog ready: {len(merged)} unique AI tools; {unlimited} unlimited-free candidates; {unknown_price} without verified pricing.')

    if len(merged) < 5000:
        raise SystemExit(f'Need 5000+ AI tools; found {len(merged)}')
    if unlimited < 100:
        raise SystemExit(f'Need 100+ unlimited-free candidates; found {unlimited}')


if __name__ == '__main__':
    main()
