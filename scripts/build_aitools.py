#!/usr/bin/env python3
"""Build the researched AI catalog into /aitools/ with local logos."""
from __future__ import annotations
import json, re, shutil, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/tools.json'; OUT=ROOT/'aitools'
PRICES={'ChatGPT':'Free · Plus $20/mo · Pro $200/mo','Claude':'Free · Pro $20/mo','Gemini':'Free · Google AI Pro $19.99/mo','Perplexity':'Free · Pro $20/mo','Grok':'Free · plans vary','Microsoft Copilot':'Free · Pro $20/mo','DeepSeek':'Free','Cursor':'Free · Pro $20/mo','Windsurf':'Free · paid plans vary','GitHub Copilot':'Paid · from $10/mo','Replit':'Free · paid plans vary','v0':'Free · paid plans vary','Lovable':'Free · paid plans vary','Bolt.new':'Free · paid plans vary','Midjourney':'Paid · plans vary','Adobe Firefly':'Free tier · paid plans vary','Ideogram':'Free tier · paid plans vary','Leonardo AI':'Free tier · paid plans vary','Canva':'Free · Pro plans available','Runway':'Free tier · paid plans vary','Sora':'Paid · eligible OpenAI plans','Kling AI':'Free tier · paid plans vary','Pika':'Free tier · paid plans vary','Luma':'Free tier · paid plans vary','HeyGen':'Free tier · paid plans vary','Synthesia':'Paid · plans vary','ElevenLabs':'Free tier · paid from $5/mo','Suno':'Free tier · paid plans vary','Udio':'Free tier · paid plans vary','Descript':'Free tier · paid plans vary','Notion AI':'Paid/add-on · plans vary','Gamma':'Free · paid plans available','NotebookLM':'Free','Genspark':'Free tier · paid plans vary','Manus':'Paid/usage plans vary','Zapier':'Free · paid plans vary','Make':'Free · paid plans vary','n8n':'Free/self-hosted · paid cloud plans','HubSpot':'Free tools · paid plans vary','Jasper':'Paid · plans vary','Grammarly':'Free · Pro plans available','QuillBot':'Free · Premium plans available','Copy.ai':'Free tier · paid plans vary','Writesonic':'Free tier · paid plans vary'}
def slug(s): return re.sub(r'^-|-$','',re.sub(r'[^a-z0-9]+','-',s.lower())) or 'tool'
def download(url,path):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 LaxmanNepal-AITools/1.0'})
        with urllib.request.urlopen(req,timeout=12) as r:
            data=r.read(512*1024)
            if data and len(data)>20: path.write_bytes(data); return True
    except Exception: pass
    return False
def local_logo(t,d):
    host=urllib.parse.urlparse(t['url']).hostname or ''
    for name,url in [('logo.ico',f'https://{host}/favicon.ico'),('logo.png',f'https://www.google.com/s2/favicons?domain={urllib.parse.quote(host)}&sz=128')]:
        if download(url,d/name): return name
    initials=''.join(x[0] for x in re.findall(r'[A-Za-z0-9]+',t['title'])[:2]).upper() or 'AI'
    (d/'logo-fallback.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><rect width="128" height="128" rx="30" fill="#111827"/><text x="64" y="75" text-anchor="middle" font-family="Arial" font-size="38" font-weight="700" fill="white">{initials}</text></svg>',encoding='utf-8')
    return 'logo-fallback.svg'
def build():
    import sys; sys.path.insert(0,str(ROOT/'scripts')); import generate_tools; generate_tools.build()
    raw=json.loads(DATA.read_text(encoding='utf-8'))
    if len(raw)<500: raise RuntimeError(f'Only {len(raw)} tools collected; refusing to publish')
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True); enriched=[]
    for rank,src_tool in enumerate(raw,1):
        t=dict(src_tool); t['trendingRank']=rank; t['price']=PRICES.get(t['title'],t.get('pricing','Check provider')); t['pricing']=t['price']; t['researchStatus']='researched' if t['title'] in PRICES else 'catalog-verified-url'
        d=OUT/slug(t['title']); d.mkdir(parents=True); logo=local_logo(t,d); t['logo']=logo
        (d/'data.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        src=ROOT/'tools'/slug(t['title'])/'index.html'
        if src.exists():
            page=src.read_text(encoding='utf-8'); marker='const tool='; start=page.find(marker); end=page.find(';const esc=',start)
            if start>=0 and end>=0: page=page[:start]+marker+json.dumps(t,ensure_ascii=False).replace('</','<\\/')+page[end:]
            page=page.replace('src="../../icon.svg"','src="logo-fallback.svg"'); page=page.replace('tool.logo||\'../../icon.svg\'','tool.logo||\'logo-fallback.svg\'')
            (d/'index.html').write_text(page,encoding='utf-8')
        enriched.append(t)
    (OUT/'index.json').write_text(json.dumps(enriched,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(enriched)} tools under /aitools with local logos')
if __name__=='__main__': build()
