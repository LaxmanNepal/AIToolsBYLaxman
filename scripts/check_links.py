#!/usr/bin/env python3
"""Check catalog provider URLs concurrently and write a machine-readable report."""
from __future__ import annotations
import concurrent.futures, json, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tools.json"
REPORT = ROOT / "link-report.json"


def check(item: dict) -> dict:
    url = item["url"]
    started = time.time()
    try:
        req = Request(url, method="HEAD", headers={"User-Agent":"LaxmanNepal-AITools-LinkChecker/1.0"})
        with urlopen(req, timeout=12) as r: status = r.status
        if status in (405, 501):
            raise RuntimeError("HEAD unsupported")
        return {"slug": item["slug"], "title": item["title"], "url": url, "ok": 200 <= status < 400, "status": status, "seconds": round(time.time()-started,2)}
    except Exception:
        try:
            req = Request(url, method="GET", headers={"User-Agent":"LaxmanNepal-AITools-LinkChecker/1.0"})
            with urlopen(req, timeout=12) as r: status = r.status
            return {"slug": item["slug"], "title": item["title"], "url": url, "ok": 200 <= status < 400, "status": status, "seconds": round(time.time()-started,2)}
        except HTTPError as e:
            return {"slug": item["slug"], "title": item["title"], "url": url, "ok": False, "status": e.code, "error": str(e)}
        except (URLError, TimeoutError, Exception) as e:
            return {"slug": item["slug"], "title": item["title"], "url": url, "ok": False, "status": None, "error": str(e)[:200]}


def main() -> None:
    tools = json.loads(DATA.read_text(encoding="utf-8"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(check, tools))
    dead = [r for r in results if not r["ok"]]
    report = {"checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "total": len(results), "ok": len(results)-len(dead), "failed": len(dead), "failure_rate": round(len(dead)/len(results),4) if results else 1, "results": results}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {len(results)} URLs: {report['ok']} reachable, {report['failed']} failed")
    # Never publish a catalog where the majority of provider URLs are dead.
    if results and len(dead) / len(results) > 0.25:
        raise SystemExit("More than 25% of provider URLs failed; refusing deployment")


if __name__ == "__main__": main()
