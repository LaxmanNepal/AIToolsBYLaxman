import json,re,urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'tools.json'
SOURCES=[
 ('AIFOXX','https://raw.githubusercontent.com/withkarann/aifoxx/main/src/data/tools.json'),
 ('AI_TOOLS_DATABASE','https://raw.githubusercontent.com/Durgesh-Vaigandla/AI-tools-database/main/data/tools.json'),
 ('SKOPX_AI_TOOLS','https://raw.githubusercontent.com/skopx/AI-tools/main/tools.json'),
 ('FREE_AI','https://raw.githubusercontent.com/chid/free-ai/main/README.md'),
]
AI=('artificial intelligence',' ai ','ai tool','ai-powered','ai powered','llm','large language','machine learning','deep learning','generative ai','genai','agent','agentic','vision','computer vision','natural language','nlp','text to image','text-to-image','text to video','text-to-video','image generation','speech recognition','speech synthesis','voice cloning','embedding','diffusion','transformer','inference','rag','multimodal','ocr','chatbot','copilot','automation','prompt','neural network','stable diffusion','generative','foundation model','ai assistant')
FREE=('unlimited free','100% free','100% forever free','free forever','completely free','fully free','no limits','unlimited access','unlimited use','free and unlimited','free offline','free locally')
LOCAL=('self-host','self hosted','self-hosted','run locally','local ai','offline ai','on-device','on device','local inference','self deploy','self-deploy','runs locally','local model','local llm','offline')
MAX_TOOLS=8000

def fetch(url):
    r=urllib.request.Request(url,headers={'User-Agent':'LaxmanNepal-AITools/6.0','Accept':'application/json,text/plain,*/*'})
    return urllib.request.urlopen(r,timeout=180).read().decode('utf-8','replace')

def clean(u):
    if not isinstance(u,str): return ''
    u=u.strip().strip('`').rstrip('.,;)')
    if not u.startswith(('http://','https://')): return ''
    try: return u if urlparse(u).netloc else ''
    except Exception: return ''

def cat(v):
    if isinstance(v,list): v=v[0] if v else 'Other AI'
    return str(v or 'Other AI').replace('_',' ').replace('-',' ').strip().title()

def flatten_source(obj):
    """Accept arrays, {tools/data/products:[...]}, or category-keyed dictionaries."""
    if isinstance(obj,list): return obj
    if not isinstance(obj,dict): return []
    for key in ('tools','data','products','items','results'):
        value=obj.get(key)
        if isinstance(value,list): return value
    out=[]
    for key,value in obj.items():
        if isinstance(value,list):
            for item in value:
                if isinstance(item,dict):
                    item=dict(item)
                    item.setdefault('category',key)
                    out.append(item)
    return out

def norm(t,source):
    if not isinstance(t,dict): return None
    md=t.get('metadata') if isinstance(t.get('metadata'),dict) else {}
    name=t.get('name') or t.get('title') or t.get('product')
    github=clean(t.get('github_url') or md.get('github_url') or t.get('source_url') or t.get('repository'))
    url=clean(t.get('url') or t.get('website') or t.get('homepage') or t.get('link') or github)
    if not name or not url: return None
    category=cat(t.get('category') or t.get('category_name') or md.get('category'))
    tags=t.get('tags') or md.get('tags') or []
    if isinstance(tags,str): tags=[x.strip() for x in re.split(r'[,|]',tags) if x.strip()]
    if not isinstance(tags,list): tags=[]
    desc=str(t.get('description') or t.get('summary') or '').strip()
    pricing=str(t.get('pricing') or t.get('price') or t.get('free_tier') or t.get('pricing_model') or '').strip()
    license_name=str(t.get('license') or md.get('license') or '').lower()
    stars=t.get('github_stars') or md.get('github_stars') or 0
    text=f' {name} {category} {desc} {" ".join(map(str,tags))} {pricing} {license_name} {github} '.lower()
    # Skopx is itself an AI-tools registry. Its records frequently omit the word "AI" from
    # individual descriptions, so use the registry provenance as an additional AI signal.
    ai_match=any(w in text for w in AI)
    if not ai_match and source!='SKOPX_AI_TOOLS': return None
    # Avoid importing obvious non-AI generic infrastructure from broad registries.
    if source=='SKOPX_AI_TOOLS' and not ai_match:
        generic=('css','javascript','typescript','react','database','networking','ebook','calendar','logging','ssl','maps','compiler','parser','testing','ui library')
        if any(g in text for g in generic) and not any(x in text for x in ('model','agent','llm','machine learning','deep learning','neural','inference','ocr','speech','vision','generative')):
            return None
    local=any(w in text for w in LOCAL)
    explicit=any(w in text for w in FREE)
    open_source=bool(t.get('open_source') or md.get('open_source') or github)
    permissive=any(w in license_name for w in ('mit','apache','bsd','mpl','isc','gpl','agpl','lgpl'))
    # Local/self-hosted open-source software is effectively unlimited from the vendor's
    # usage-limit perspective; hosted free tiers are only unlimited when explicitly stated.
    unlimited=explicit or local or (open_source and permissive and github!='')
    return {
        'title':str(name).strip(),
        'description':desc or f'{name} — AI-related tool or project.',
        'url':url,
        'logo':t.get('logo') or t.get('icon') or f'{url.rstrip("/")}/favicon.ico',
        'pricing':'Unlimited Free' if unlimited else (pricing or 'Pricing not publicly verified'),
        'category':'Unlimited Free AI Tools' if unlimited else category,
        'original_category':category,
        'tags':tags,
        'self_hostable':local or (open_source and permissive),
        'open_source':open_source,
        'license':t.get('license') or md.get('license'),
        'github_url':github,
        'github_stars':stars,
        'pricing_verified':bool(pricing),
        'unlimited_free_verified':unlimited,
        'source':source,
    }

def parse_md(s):
    out=[]
    for line in s.splitlines():
        m=re.match(r'^\s*[-*]\s+\*?\*?([^–—-]{2,80})\*?\*?\s*[-–—:]\s+(.+)$',line)
        if m:
            name,rest=m.group(1).strip(' *`'),m.group(2).strip()
            u=re.search(r'https?://[^\s)]+',rest)
            if u and any(w in (name+' '+rest).lower() for w in AI):
                out.append({'name':name,'description':rest,'category':'Free AI Tools','url':u.group(0).rstrip('.,'),'pricing':'Free'})
    return out

def main():
    try: local=json.loads(DATA.read_text(encoding='utf-8'))
    except Exception: local=[]
    merged=[]; seen=set()
    def add(x,source):
        t=norm(x,source)
        if not t: return 0
        k=t['url'].rstrip('/').lower()
        if k in seen: return 0
        seen.add(k); merged.append(t); return 1
    for x in local: add(x,'local')
    for source,url in SOURCES:
        try:
            raw=fetch(url)
            ext=parse_md(raw) if url.endswith('.md') else flatten_source(json.loads(raw))
            n=sum(add(x,source) for x in ext)
            print(f'{source}: imported {n}')
        except Exception as e:
            print(f'{source}: warning: {e}')
    # Prefer verified/free/self-hosted entries, then popularity, while preserving diversity.
    merged.sort(key=lambda x:(x.get('category')!='Unlimited Free AI Tools',not x.get('pricing_verified'),not x.get('open_source'),-int(x.get('github_stars') or 0),str(x.get('title','')).lower()))
    merged=merged[:MAX_TOOLS]
    DATA.write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    unlimited=sum(x.get('category')=='Unlimited Free AI Tools' for x in merged)
    unknown=sum(not x.get('pricing_verified') for x in merged)
    print(f'Catalog ready: {len(merged)} AI tools; {unlimited} unlimited-free; {unknown} without verified pricing.')
    if len(merged)<5000: raise SystemExit(f'Need 5000+ AI tools; found {len(merged)}')
    if unlimited<100: raise SystemExit(f'Need 100+ unlimited-free tools; found {unlimited}')

if __name__=='__main__': main()
