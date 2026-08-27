import json,re,urllib.request
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'/'tools.json'; EVERYTHING=ROOT/'everything.json'
SOURCES=[('AIFOXX','https://raw.githubusercontent.com/withkarann/aifoxx/main/src/data/tools.json'),('AI_TOOLS_DATABASE','https://raw.githubusercontent.com/Durgesh-Vaigandla/AI-tools-database/main/data/tools.json'),('SKOPX_AI_TOOLS','https://raw.githubusercontent.com/skopx/AI-tools/main/tools.json'),('FREE_AI','https://raw.githubusercontent.com/chid/free-ai/main/README.md'),('AI_TOOLS_19K','https://raw.githubusercontent.com/lakey009/AI-Tools-List/main/AIToolsList.json')]
AI=('artificial intelligence',' ai ','ai tool','ai-powered','ai powered','llm','large language','machine learning','deep learning','generative ai','genai','agent','agentic','vision','computer vision','natural language','nlp','text to image','text-to-image','text to video','text-to-video','image generation','speech recognition','speech synthesis','voice cloning','embedding','diffusion','transformer','inference','rag','multimodal','ocr','chatbot','copilot','automation','prompt','neural network','stable diffusion','foundation model','ai assistant','generative')
FREE=('unlimited free','100% free','100% forever free','free forever','completely free','fully free','no limits','unlimited access','unlimited use','free and unlimited','free offline','free locally')
LOCAL=('self-host','self hosted','self-hosted','run locally','local ai','offline ai','on-device','on device','local inference','self deploy','self-deploy','runs locally','local model','local llm','offline')
MAX_TOOLS=10000
def fetch(url):
 r=urllib.request.Request(url,headers={'User-Agent':'LaxmanNepal-AITools/7.0','Accept':'application/json,text/plain,*/*'}); return urllib.request.urlopen(r,timeout=180).read().decode('utf-8','replace')
def clean(u):
 if not isinstance(u,str): return ''
 u=u.strip().strip('`').rstrip('.,;)')
 try: return u if u.startswith(('http://','https://')) and urlparse(u).netloc else ''
 except: return ''
def cat(v):
 if isinstance(v,list): v=v[0] if v else 'Other AI'
 return str(v or 'Other AI').replace('_',' ').replace('-',' ').strip().title()
def flatten(o):
 if isinstance(o,list): return o
 if not isinstance(o,dict): return []
 for k in ('tools','data','products','items','results'):
  if isinstance(o.get(k),list): return o[k]
 out=[]
 for k,v in o.items():
  if isinstance(v,list):
   for x in v:
    if isinstance(x,dict): x=dict(x); x.setdefault('category',k); out.append(x)
 return out
def norm(t,source):
 if not isinstance(t,dict): return None
 md=t.get('metadata') if isinstance(t.get('metadata'),dict) else {}
 name=t.get('name') or t.get('title') or t.get('product') or t.get('handle'); github=clean(t.get('github_url') or md.get('github_url') or t.get('source_url') or t.get('repository')); url=clean(t.get('url') or t.get('website') or t.get('homepage') or t.get('link') or github)
 if not name or not url:return None
 category=cat(t.get('category') or t.get('category_name') or md.get('category')); tags=t.get('tags') or md.get('tags') or []; tags=[x.strip() for x in re.split(r'[,|]',tags) if x.strip()] if isinstance(tags,str) else tags if isinstance(tags,list) else []
 desc=str(t.get('description') or t.get('summary') or '').strip(); pricing=str(t.get('pricing') or t.get('price') or t.get('free_tier') or t.get('pricing_model') or '').strip(); lic=str(t.get('license') or md.get('license') or '').lower(); stars=t.get('github_stars') or md.get('github_stars') or 0; text=f' {name} {category} {desc} {" ".join(map(str,tags))} {pricing} {lic} {github} '.lower()
 ai_match=any(w in text for w in AI)
 if not ai_match and source!='SKOPX_AI_TOOLS': return None
 local=any(w in text for w in LOCAL); explicit=any(w in text for w in FREE); opens=bool(t.get('open_source') or md.get('open_source') or github); permissive=any(w in lic for w in ('mit','apache','bsd','mpl','isc','gpl','agpl','lgpl')); unlimited=explicit or local or (opens and permissive and github!='')
 return {'id':re.sub(r'[^a-z0-9]+','-',str(name).lower()).strip('-'),'title':str(name).strip(),'description':desc or f'{name} — AI-related tool or project.','url':url,'logo':t.get('logo') or t.get('icon') or f'{url.rstrip("/")}/favicon.ico','pricing':'Unlimited Free' if unlimited else pricing or 'Pricing not publicly verified','category':'Unlimited Free AI Tools' if unlimited else category,'original_category':category,'tags':tags,'self_hostable':local or (opens and permissive),'open_source':opens,'license':t.get('license') or md.get('license'),'github_url':github,'github_stars':stars,'pricing_verified':bool(pricing),'unlimited_free_verified':unlimited,'source':source}
def parse_md(s):
 out=[]
 for line in s.splitlines():
  m=re.match(r'^\s*[-*]\s+\*?\*?([^–—-]{2,80})\*?\*?\s*[-–—:]\s+(.+)$',line)
  if m:
   n,r=m.group(1).strip(' *`'),m.group(2).strip(); u=re.search(r'https?://[^\s)]+',r)
   if u and any(w in (n+' '+r).lower() for w in AI):out.append({'name':n,'description':r,'category':'Free AI Tools','url':u.group(0).rstrip('.,'),'pricing':'Free'})
 return out
def main():
 try: local=json.loads(DATA.read_text(encoding='utf-8'))
 except: local=[]
 merged=[];seen=set()
 def add(x,src):
  t=norm(x,src)
  if not t:return 0
  k=t['url'].rstrip('/').lower()
  if k in seen:return 0
  seen.add(k);merged.append(t);return 1
 for x in local:add(x,'local')
 for src,u in SOURCES:
  try:
   raw=fetch(u); ext=parse_md(raw) if u.endswith('.md') else flatten(json.loads(raw)); print(f'{src}: imported {sum(add(x,src) for x in ext)}')
  except Exception as e:print(f'{src}: warning: {e}')
 merged.sort(key=lambda x:(x.get('category')!='Unlimited Free AI Tools',not x.get('pricing_verified'),not x.get('open_source'),-int(x.get('github_stars') or 0),str(x.get('title','')).lower()));merged=merged[:MAX_TOOLS]
 DATA.write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 unlimited=sum(x.get('unlimited_free_verified') for x in merged); now=datetime.now(timezone.utc).isoformat()
 EVERYTHING.write_text(json.dumps({'metadata':{'name':'Laxman Nepal AI Tools Directory','version':'7.0','last_updated':now,'total_tools':len(merged),'unlimited_free_tools':unlimited},'tools':merged},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'Catalog ready: {len(merged)} tools; {unlimited} unlimited-free.')
 if len(merged)<5000:raise SystemExit(f'Need 5000+ AI tools; found {len(merged)}')
 if unlimited<100:raise SystemExit(f'Need 100+ unlimited-free tools; found {unlimited}')
if __name__=='__main__':main()
