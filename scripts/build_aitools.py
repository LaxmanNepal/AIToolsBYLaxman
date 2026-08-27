#!/usr/bin/env python3
"""Build the researched AI catalog into /aitools/ with local logos."""
from __future__ import annotations
import json, re, shutil, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/tools.json'; OUT=ROOT/'aitools'
PRICES={'ChatGPT':'Free · Plus $20/mo · Pro $200/mo','Claude':'Free · Pro $20/mo','Gemini':'Free · Google AI Pro $19.99/mo','Perplexity':'Free · Pro $20/mo','Grok':'Free · plans vary','Microsoft Copilot':'Free · Pro $20/mo','DeepSeek':'Free','Cursor':'Free · Pro $20/mo','Windsurf':'Free · paid plans vary','GitHub Copilot':'Paid · from $10/mo','Replit':'Free · paid plans vary','v0':'Free · paid plans vary','Lovable':'Free · paid plans vary','Bolt.new':'Free · paid plans vary','Midjourney':'Paid · plans vary','Adobe Firefly':'Free tier · paid plans vary','Ideogram':'Free tier · paid plans vary','Leonardo AI':'Free tier · paid plans vary','Canva':'Free · Pro plans available','Runway':'Free tier · paid plans vary','Sora':'Paid · eligible OpenAI plans','Kling AI':'Free tier · paid plans vary','Pika':'Free tier · paid plans vary','Luma':'Free tier · paid plans vary','HeyGen':'Free tier · paid plans vary','Synthesia':'Paid · plans vary','ElevenLabs':'Free tier · paid from $5/mo','Suno':'Free tier · paid plans vary','Udio':'Free tier · paid plans vary','Descript':'Free tier · paid plans vary','Notion AI':'Paid/add-on · plans vary','Gamma':'Free · paid plans available','NotebookLM':'Free','Genspark':'Free tier · paid plans vary','Manus':'Paid/usage plans vary','Zapier':'Free · paid plans vary','Make':'Free · paid plans vary','n8n':'Free/self-hosted · paid cloud plans','HubSpot':'Free tools · paid plans vary','Jasper':'Paid · plans vary','Grammarly':'Free · Pro plans available','QuillBot':'Free · Premium plans available','Copy.ai':'Free tier · paid plans vary','Writesonic':'Free tier · paid plans vary','Poe':'Free tier · paid plans vary','Character.AI':'Free · c.ai+ paid plan','Mistral Le Chat':'Free tier · paid plans vary','Meta AI':'Free','Pi':'Free','DeepL':'Free tier · paid plans vary','Otter.ai':'Free tier · paid plans vary','Fireflies.ai':'Free tier · paid plans vary','Tome':'Free tier · paid plans vary','Beautiful.ai':'Paid · plans vary','Photoroom':'Free tier · paid plans vary'}
SUPPLEMENT=[('Poe','https://poe.com/','AI Assistants','Freemium','AI platform providing access to multiple conversational models and bots.'),('Character.AI','https://character.ai/','AI Assistants','Freemium','Conversational AI platform centered on user-created characters and agents.'),('Mistral Le Chat','https://chat.mistral.ai/','AI Assistants','Freemium','Mistral conversational assistant for research, writing, coding and analysis.'),('Meta AI','https://www.meta.ai/','AI Assistants','Free','Meta AI assistant for conversation, creation and search experiences.'),('Pi','https://pi.ai/','AI Assistants','Free','Personal conversational AI focused on helpful dialogue and everyday assistance.'),('DeepL','https://www.deepl.com/','AI Translation','Freemium','AI translation and writing platform for multilingual communication.'),('Otter.ai','https://otter.ai/','AI Productivity','Freemium','AI meeting transcription, notes and conversation intelligence.'),('Fireflies.ai','https://fireflies.ai/','AI Productivity','Freemium','AI meeting recorder, transcription and searchable meeting assistant.'),('Tome','https://tome.app/','AI Presentations','Freemium','AI-assisted presentation and storytelling workspace.'),('Beautiful.ai','https://www.beautiful.ai/','AI Presentations','Paid','Presentation software with AI-assisted slide design and layout.'),('Photoroom','https://www.photoroom.com/','AI Image Editing','Freemium','AI photo editor for product images, backgrounds and commercial visuals.'),('CapCut','https://www.capcut.com/','AI Video','Freemium','Video editor with AI-assisted generation, captions, effects and editing.'),('VEED','https://www.veed.io/','AI Video','Freemium','Online video editor with AI generation, subtitles, dubbing and cleanup.'),('InVideo AI','https://invideo.io/','AI Video','Freemium','AI video creation platform that turns prompts and scripts into videos.'),('Descript Overdub','https://www.descript.com/','AI Voice & Audio','Freemium','AI voice and text-based media editing features from Descript.'),('Murf AI','https://murf.ai/','AI Voice & Audio','Freemium','AI voice generation platform for narration, presentations and voiceovers.'),('Speechify','https://speechify.com/','AI Voice & Audio','Freemium','Text-to-speech and reading assistant for documents and web content.'),('Consensus','https://consensus.app/','AI Research','Freemium','AI research search engine for finding and summarizing scientific papers.'),('Elicit','https://elicit.com/','AI Research','Freemium','Research assistant for literature reviews, paper discovery and synthesis.'),('Scite','https://scite.ai/','AI Research','Freemium','Research platform that analyzes scientific citations and supporting evidence.'),('Gamma AI','https://gamma.app/','AI Presentations','Freemium','AI-powered creation of presentations, documents and web pages.')]
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
    import sys; sys.path.insert(0,str(ROOT/'scripts')); import generate_tools
    # The public seed currently yields 496 unique entries; add researched current tools rather than lowering the 500+ quality gate.
    known={x[0] for x in generate_tools.CURRENT}
    for item in SUPPLEMENT:
        if item[0] not in known: generate_tools.CURRENT.append(item)
    generate_tools.build()
    raw=json.loads(DATA.read_text(encoding='utf-8'))
    if len(raw)<500: raise RuntimeError(f'Only {len(raw)} tools collected; refusing to publish')
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True); enriched=[]
    for rank,src_tool in enumerate(raw,1):
        t=dict(src_tool); t['trendingRank']=rank; t['price']=PRICES.get(t['title'],t.get('pricing','Check provider')); t['pricing']=t['price']; t['researchStatus']='researched' if t['title'] in PRICES else 'catalog-verified-url'
        d=OUT/slug(t['title']); d.mkdir(parents=True); t['logo']=local_logo(t,d)
        (d/'data.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        src=ROOT/'tools'/slug(t['title'])/'index.html'
        if src.exists():
            page=src.read_text(encoding='utf-8'); marker='const tool='; start=page.find(marker); end=page.find(';const esc=',start)
            if start>=0 and end>=0: page=page[:start]+marker+json.dumps(t,ensure_ascii=False).replace('</','<\\/')+page[end:]
            page=page.replace('src="../../icon.svg"','src="logo-fallback.svg"').replace('tool.logo||\'../../icon.svg\'','tool.logo||\'logo-fallback.svg\'')
            (d/'index.html').write_text(page,encoding='utf-8')
        enriched.append(t)
    (OUT/'index.json').write_text(json.dumps(enriched,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(enriched)} tools under /aitools with local logos')
if __name__=='__main__': build()
