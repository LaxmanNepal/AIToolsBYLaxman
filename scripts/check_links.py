#!/usr/bin/env python3
from __future__ import annotations
import concurrent.futures,json,time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/tools.json'; REPORT=ROOT/'link-report.json'; LIMIT=500
def reachable(status): return status is not None and (200<=status<400 or status in {401,403,429})
def check(item):
    url=item['url']; started=time.time(); result={'slug':item['slug'],'title':item['title'],'url':url,'ok':False,'status':None}
    for method in ('HEAD','GET'):
        try:
            req=Request(url,method=method,headers={'User-Agent':'LaxmanNepal-AITools-LinkChecker/1.0'})
            with urlopen(req,timeout=8) as r: result['status']=r.status; result['ok']=reachable(r.status); break
        except HTTPError as e:
            result['status']=e.code
            if method=='GET': result['ok']=reachable(e.code)
            if e.code not in {405,429,500,502,503,504}: break
        except (URLError,TimeoutError):
            if method=='GET': result['error']='network/timeout'
        except Exception as e:
            if method=='GET': result['error']=str(e)[:200]
    result['seconds']=round(time.time()-started,2); result['needs_review']=not result['ok'] and result.get('status') in {401,403,429,500,502,503,504}; return result
def main():
    tools=json.loads(DATA.read_text(encoding='utf-8')); by_domain={}
    for t in tools:
        domain=(urlparse(t['url']).hostname or '').lower().removeprefix('www.')
        by_domain.setdefault(domain,t)
    sample=list(by_domain.values())[:LIMIT]
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as pool: results=list(pool.map(check,sample))
    dead=[r for r in results if not r['ok'] and not r.get('needs_review')]; review=[r for r in results if r.get('needs_review')]
    report={'checked_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'catalog_total':len(tools),'unique_domains':len(by_domain),'sample_limit':LIMIT,'checked':len(results),'ok':len(results)-len(dead)-len(review),'needs_review':len(review),'failed':len(dead),'failure_rate':round(len(dead)/len(results),4) if results else 1,'results':results}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(f"Checked {len(results)} provider domains from {len(tools)} tools: {report['ok']} reachable, {report['needs_review']} review, {report['failed']} dead")
    if results and len(dead)/len(results)>.25: raise SystemExit('More than 25% of checked provider domains are confirmed dead; refusing deployment')
if __name__=='__main__': main()
