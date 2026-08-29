#!/usr/bin/env python3
from __future__ import annotations
import html,json,re,shutil
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/tools.json'; TOOLS=ROOT/'tools'; CATEGORIES=ROOT/'categories'; BASE_URL='https://ai.laxmannepal.com.np'
def slugify(v): return re.sub(r'^-|-$','',re.sub(r'[^a-z0-9]+','-',v.lower().strip())) or 'tools'
def load_tools():
    payload=json.loads(DATA.read_text(encoding='utf-8'))
    tools=payload.get('tools',[]) if isinstance(payload,dict) else payload
    if not isinstance(tools,list): raise RuntimeError('data/tools.json must contain a tools array')
    return tools
def compact_index(tools):
    fields=('title','slug','category','pricing','logo','url','trendingRank','source')
    (TOOLS/'index.json').write_text(json.dumps([{k:t.get(k) for k in fields} for t in tools],ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def build_categories(tools):
    groups={}
    for t in tools: groups.setdefault(str(t.get('category') or 'AI Tools').strip(),[]).append(t)
    cats=[]; CATEGORIES.mkdir(exist_ok=True)
    for child in CATEGORIES.iterdir():
        if child.is_dir(): shutil.rmtree(child)
    for name,items in sorted(groups.items(),key=lambda x:(-len(x[1]),x[0].lower())):
        slug=slugify(name); cats.append({'name':name,'slug':slug,'count':len(items)})
        cards=''.join(f'<li><a href="../../tools/{quote(str(t["slug"]))}/"><strong>{html.escape(str(t["title"]))}</strong><span>{html.escape(str(t.get("pricing") or "Check provider"))}</span></a></li>' for t in items)
        page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(name)} — AI Tools | Laxman Nepal</title><meta name="description" content="Explore {len(items)} {html.escape(name)} tools in the Laxman Nepal AI directory."><link rel="canonical" href="{BASE_URL}/categories/{slug}/"><meta property="og:title" content="{html.escape(name)} — AI Tools"><meta property="og:description" content="Explore {len(items)} AI tools in this category."><meta property="og:type" content="website"><style>body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,Inter,system-ui,sans-serif;background:#f5f7fb;color:#101114}}main{{max-width:1050px;margin:auto;padding:28px 16px 60px}}header,section{{background:#ffffffc9;border:1px solid #fff;border-radius:24px;padding:24px;box-shadow:0 18px 55px #00000010;backdrop-filter:blur(22px)}}h1{{font-size:clamp(38px,7vw,68px);line-height:.95;letter-spacing:-.06em;margin:8px 0}}p{{color:#667085;line-height:1.6}}ul{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px}}li a{{display:flex;justify-content:space-between;gap:8px;padding:15px;border-radius:16px;background:#ffffffaa;border:1px solid #fff}}li span{{color:#667085;font-size:12px}}@media(max-width:700px){{ul{{grid-template-columns:1fr 1fr}}}}@media(max-width:480px){{ul{{grid-template-columns:1fr}}}}</style></head><body><main><header><a href="../../">← AI Tools</a><h1>{html.escape(name)}</h1><p>{len(items)} tools in this category. Browse individual pages for pricing, use cases, limitations and prompts.</p></header><section><h2>Tools in {html.escape(name)}</h2><ul>{cards}</ul></section></main></body></html>'''
        d=CATEGORIES/slug; d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(page,encoding='utf-8')
    hub_cards=''.join(f'<a class="card" href="{quote(c["slug"])}/"><strong>{html.escape(c["name"])}</strong><span>{c["count"]} tools →</span></a>' for c in cats)
    hub=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Tool Categories — Laxman Nepal</title><meta name="description" content="Browse AI tools by category."><link rel="canonical" href="{BASE_URL}/categories/"><style>body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,Inter,system-ui,sans-serif;background:#f5f7fb;color:#101114}}main{{max-width:1100px;margin:auto;padding:28px 16px 60px}}header,section{{background:#ffffffc9;border:1px solid #fff;border-radius:24px;padding:24px;box-shadow:0 18px 55px #00000010}}h1{{font-size:clamp(40px,7vw,72px);line-height:.95;letter-spacing:-.06em;margin:10px 0}}p{{color:#667085;line-height:1.6}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin-top:18px}}.card{{display:block;padding:18px;border-radius:18px;background:#ffffffaa;border:1px solid #fff}}.card strong,.card span{{display:block}}.card span{{margin-top:6px;color:#667085;font-size:12px}}@media(max-width:700px){{.grid{{grid-template-columns:1fr 1fr}}}}@media(max-width:450px){{.grid{{grid-template-columns:1fr}}}}</style></head><body><main><header><a href="../">← AI Tools</a><h1>AI tool categories.</h1><p>Browse crawlable category pages instead of relying only on JavaScript filters.</p></header><section><div class="grid">{hub_cards}</div></section></main></body></html>'''
    (CATEGORIES/'index.html').write_text(hub,encoding='utf-8'); (ROOT/'data/categories.json').write_text(json.dumps(cats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); return cats
def build_seo(tools,cats):
    (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /go/\n\nSitemap: {BASE_URL}/sitemap.xml\n',encoding='utf-8')
    urls=[BASE_URL+'/',BASE_URL+'/trending/',BASE_URL+'/categories/',BASE_URL+'/compare/',BASE_URL+'/search/']+[f'{BASE_URL}/categories/{quote(str(c["slug"]))}/' for c in cats]+[f'{BASE_URL}/tools/{quote(str(t["slug"]))}/' for t in tools if t.get('slug')]
    xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']+[f'  <url><loc>{html.escape(u)}</loc></url>' for u in urls]+['</urlset>']; (ROOT/'sitemap.xml').write_text('\n'.join(xml)+'\n',encoding='utf-8')
def main():
    import sys; sys.path.insert(0,str(ROOT/'scripts')); import generate_tools; generate_tools.build(); tools=load_tools(); assert len(tools)>=500,f'Build produced only {len(tools)} tools'; compact_index(tools); cats=build_categories(tools); build_seo(tools,cats); print(f'Production build complete: {len(tools)} tools, {len(cats)} categories')
if __name__=='__main__': main()
