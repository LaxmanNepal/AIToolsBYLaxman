#!/usr/bin/env python3
"""Build a 500+ AI-tool catalog and static detail pages."""
from __future__ import annotations
import datetime as dt, html, json, re, shutil, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/tools.json'; TOOLS_DIR=ROOT/'tools'
SOURCE_URL='https://www.indiaseva.com/500-plus-AI-tools-and-tutorials/'; TODAY=dt.date.today().isoformat()
CURRENT=[
('ChatGPT','https://chatgpt.com/','AI Assistants','Freemium',"OpenAI's general-purpose AI assistant for writing, reasoning, coding, images, research and everyday tasks."),('Claude','https://claude.ai/','AI Assistants','Freemium',"Anthropic's AI assistant for reasoning, writing, analysis, coding and long-context work."),('Gemini','https://gemini.google.com/','AI Assistants','Freemium',"Google's multimodal AI assistant for writing, research, coding, images and productivity."),('Perplexity','https://www.perplexity.ai/','AI Search & Research','Freemium','AI search and research assistant that answers questions with web sources and citations.'),('Grok','https://grok.com/','AI Assistants','Freemium',"xAI's conversational assistant for reasoning, research, coding and current-information tasks."),('Microsoft Copilot','https://copilot.microsoft.com/','AI Assistants','Freemium',"Microsoft's AI assistant for conversation, web research, writing and productivity."),('DeepSeek','https://chat.deepseek.com/','AI Assistants','Free','AI assistant known for strong reasoning and coding capabilities with free access options.'),('Cursor','https://www.cursor.com/','AI Coding','Freemium','AI-first code editor that understands a project codebase and helps write, refactor and debug code.'),('Windsurf','https://windsurf.com/','AI Coding','Freemium','AI-powered coding environment with agentic assistance for building and modifying software.'),('GitHub Copilot','https://github.com/features/copilot','AI Coding','Paid','AI coding assistant that provides code completion, chat and agentic development features.'),('Replit','https://replit.com/','AI Coding','Freemium','Browser-based development platform with AI-assisted coding, app generation and deployment.'),('v0','https://v0.dev/','AI Coding','Freemium','AI interface and application generator from Vercel for creating web UI and code from prompts.'),('Lovable','https://lovable.dev/','AI App Builders','Freemium','Prompt-driven app builder for creating full-stack web applications.'),('Bolt.new','https://bolt.new/','AI App Builders','Freemium','Browser-based AI development environment for generating and shipping web applications.'),('Midjourney','https://www.midjourney.com/','AI Image Generation','Paid','AI image creation platform focused on high-quality artistic and photorealistic visuals.'),('Adobe Firefly','https://firefly.adobe.com/','AI Image Generation','Freemium',"Adobe's generative AI suite for images, text effects, design and creative workflows."),('Ideogram','https://ideogram.ai/','AI Image Generation','Freemium','Image generation platform particularly strong at readable text inside generated images.'),('Leonardo AI','https://leonardo.ai/','AI Image Generation','Freemium','Creative AI platform for image generation, editing, design and visual asset creation.'),('FLUX','https://blackforestlabs.ai/','AI Image Generation','Paid',"Black Forest Labs' family of image-generation models and services."),('Canva','https://www.canva.com/','AI Design','Freemium','Visual design platform with AI tools for presentations, graphics, images, copy and layouts.'),('Runway','https://runwayml.com/','AI Video','Freemium','Generative video platform for creating, transforming and editing video with AI.'),('Sora','https://sora.com/','AI Video','Paid','OpenAI video generation system for creating videos from text and visual prompts.'),('Kling AI','https://klingai.com/','AI Video','Freemium','Generative video platform for text-to-video, image-to-video and creative video effects.'),('Pika','https://pika.art/','AI Video','Freemium','AI video creation platform for generating and transforming short-form videos.'),('Luma','https://lumalabs.ai/','AI Video','Freemium','Generative media platform for video and visual creation, including Dream Machine.'),('HeyGen','https://www.heygen.com/','AI Avatars','Freemium','AI avatar and video platform for presenter videos, localization and voice-driven content.'),('Synthesia','https://www.synthesia.io/','AI Avatars','Paid','Business video platform for creating presenter-led videos with AI avatars and voices.'),('ElevenLabs','https://elevenlabs.io/','AI Voice & Audio','Freemium','AI voice platform for realistic speech synthesis, voice design, dubbing and audio workflows.'),('Suno','https://suno.com/','AI Music','Freemium','Generative music platform that creates songs from natural-language prompts.'),('Udio','https://www.udio.com/','AI Music','Freemium','AI music generation service for creating songs and musical ideas from prompts.'),('Descript','https://www.descript.com/','AI Audio & Video','Freemium','AI-powered audio and video editor that lets creators edit media through text and automated tools.'),('Notion AI','https://www.notion.com/product/ai','AI Productivity','Paid','AI features inside Notion for writing, summarizing, searching and working with workspace knowledge.'),('Gamma','https://gamma.app/','AI Presentations','Freemium','AI workspace for generating presentations, documents and visual web pages.'),('NotebookLM','https://notebooklm.google.com/','AI Research & Knowledge','Free',"Google's source-grounded research notebook for asking questions and generating summaries from provided sources."),('Genspark','https://www.genspark.ai/','AI Agents','Freemium','AI workspace that combines search, research and agentic task execution.'),('Manus','https://manus.im/','AI Agents','Paid','General-purpose AI agent designed to plan and execute multi-step tasks.'),('Zapier','https://zapier.com/','AI Automation','Freemium','Automation platform connecting apps and AI steps into repeatable workflows.'),('Make','https://www.make.com/','AI Automation','Freemium','Visual automation platform for connecting services, APIs and AI-powered workflows.'),('n8n','https://n8n.io/','AI Automation','Freemium','Workflow automation platform with flexible integrations and AI agent capabilities.'),('HubSpot','https://www.hubspot.com/','AI Marketing & Sales','Freemium','CRM and marketing platform with AI-assisted sales, marketing, content and customer-service workflows.'),('Jasper','https://www.jasper.ai/','AI Writing & Marketing','Paid','AI marketing platform for creating on-brand campaigns, content and marketing workflows.'),('Grammarly','https://www.grammarly.com/','AI Writing','Freemium','Writing assistant for grammar, clarity, tone and generative writing support.'),('QuillBot','https://quillbot.com/','AI Writing','Freemium','Writing toolkit for paraphrasing, summarization, grammar and citation-related tasks.'),('Copy.ai','https://www.copy.ai/','AI Writing & Marketing','Freemium','AI platform for marketing copy, sales workflows and content generation.'),('Writesonic','https://writesonic.com/','AI Writing & SEO','Freemium','AI content and search-optimization platform for articles, marketing copy and research.')]
KEYWORDS={'AI Image Generation':['image','art','photo','logo','portrait','background'],'AI Video':['video','avatar','animation','clip','film','visual'],'AI Voice & Audio':['voice','audio','speech','podcast','sound','transcri'],'AI Writing':['write','writing','copy','text','content','essay','grammar','paraphr'],'AI Coding':['code','coding','developer','program','software','github','excel','sheet'],'AI Research':['research','paper','summar','search','knowledge','academic'],'AI Education':['education','student','tutor','quiz','learn','teacher','school'],'AI Marketing':['marketing','seo','sales','social','lead','advert','brand'],'AI Productivity':['meeting','email','note','calendar','productivity','task','workflow'],'AI Business':['business','finance','data','crm','analytics','career','resume'],'AI Automation':['automation','agent','assistant','bot','workflow']}

def slugify(v): return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+','-',v.lower().strip())) or 'tool'
def favicon(url):
    host=urllib.parse.urlparse(url).hostname or ''; return f'https://www.google.com/s2/favicons?domain={urllib.parse.quote(host)}&sz=128'
def category_for(name,desc):
    text=f'{name} {desc}'.lower(); best='AI Tools'; score=0
    for cat,words in KEYWORDS.items():
        s=sum(w in text for w in words)
        if s>score: best,score=cat,s
    return best
def pricing_for(name):
    return dict((n,p) for n,p in [(x[0],x[3]) for x in CURRENT]).get(name,'Check provider')
def parse_seed(raw):
    from bs4 import BeautifulSoup
    lines=[re.sub(r'\s+',' ',x).strip() for x in BeautifulSoup(raw,'html.parser').get_text('\n').splitlines()]
    lines=[x for x in lines if x]; records=[]; i=0
    while i<len(lines):
        if re.fullmatch(r'\d{1,3}',lines[i]):
            n=int(lines[i])
            if 1<=n<=510 and i+3<len(lines):
                title,desc=lines[i+1],lines[i+2]; url=None; j=i+3
                while j<min(i+8,len(lines)):
                    m=re.search(r'https?://[^\s]+',lines[j])
                    if m: url=m.group(0).rstrip(').,;"'); break
                    j+=1
                if url and title and not title.startswith('http'):
                    low=f'{title} {url}'.lower()
                    if not any(x in low for x in ('youtube.com','youtu.be','twitter.com','x.com','tiktok.com')) and 'tutorial' not in title.lower():
                        records.append({'title':title,'url':url,'description':desc}); i=j
        i+=1
    out=[]; seen=set()
    for r in records:
        key=(slugify(r['title']),urllib.parse.urlparse(r['url']).netloc.lower())
        if key not in seen: seen.add(key); out.append(r)
    return out
def entry(name,url,cat,price,desc,rank):
    gh='github.com' in (urllib.parse.urlparse(url).hostname or '').lower()
    return {'title':name,'slug':slugify(name),'url':url,'logo':favicon(url),'category':cat,'pricing':price,'description':desc[:500],'benefits':['Fast to try with a focused workflow','Useful for its target use case','Can reduce repetitive work'],'limitations':['Free or trial limits may apply','Quality depends on inputs and model capabilities','Always review important outputs'],'source':'github' if gh else 'web','trendingRank':rank,'lastVerified':TODAY}
def build():
    DATA.parent.mkdir(parents=True,exist_ok=True)
    try:
        req=urllib.request.Request(SOURCE_URL,headers={'User-Agent':'LaxmanNepal-AITools/1.0'})
        with urllib.request.urlopen(req,timeout=30) as r: seed=parse_seed(r.read().decode('utf-8','ignore'))
    except Exception as exc:
        print(f'Seed fetch failed: {exc}'); seed=[]
    entries=[]; seen=set(); rank=1
    for name,url,cat,price,desc in CURRENT:
        k=slugify(name)
        if k not in seen: entries.append(entry(name,url,cat,price,desc,rank)); seen.add(k); rank+=1
    for r in seed:
        k=slugify(r['title'])
        if k in seen or len(entries)>=550: continue
        entries.append(entry(r['title'],r['url'],category_for(r['title'],r['description']),pricing_for(r['title']),r['description'],rank)); seen.add(k); rank+=1
    if len(entries)<500: raise RuntimeError(f'Only {len(entries)} tools collected; refusing to publish an undersized catalog')
    DATA.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    TOOLS_DIR.mkdir(exist_ok=True)
    for child in TOOLS_DIR.iterdir():
        if child.is_dir(): shutil.rmtree(child)
    template=(ROOT/'scripts/tool_page.html').read_text(encoding='utf-8')
    for tool in entries:
        d=TOOLS_DIR/tool['slug']; d.mkdir(parents=True,exist_ok=True)
        page=template.replace('__TOOL_JSON__',json.dumps(tool,ensure_ascii=False).replace('</','<\\/'))
        (d/'index.html').write_text(page,encoding='utf-8')
    print(f'Generated {len(entries)} AI tools and {len(entries)} detail pages')
if __name__=='__main__': build()
