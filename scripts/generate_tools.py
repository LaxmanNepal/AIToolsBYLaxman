#!/usr/bin/env python3
"""Build the static AI-tools site from the single canonical data/tools.json file."""
from __future__ import annotations
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tools.json"
TOOLS = ROOT / "tools"
GO = ROOT / "go"
TODAY = dt.date.today().isoformat()
BASE = "https://ai.laxmannepal.com.np"


def slugify(value: str) -> str:
    value = value.lower().strip()
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", value)) or "tool"


def normalize(raw: list[dict]) -> list[dict]:
    out, used = [], set()
    for item in raw:
        title = str(item.get("title") or "").strip()
        url = str(item.get("url") or "").strip()
        if not title or not url or urlparse(url).scheme not in {"http", "https"}:
            continue
        base = slugify(str(item.get("slug") or title))
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        category = str(item.get("category") or "AI Tools").strip()
        price = str(item.get("pricing") or "Check provider").strip()
        record = dict(item)
        record.update({
            "title": title,
            "slug": slug,
            "url": url,
            "shortUrl": f"{BASE}/go/{slug}/",
            "category": category,
            "pricing": price,
            "description": str(item.get("description") or f"{title} — AI tool.")[:500],
            "lastVerified": str(item.get("lastVerified") or TODAY),
        })
        record.setdefault("source", "web")
        record.setdefault("useCases", record.get("benefits", []))
        record.setdefault("benefits", [])
        record.setdefault("limitations", [])
        record.setdefault("prompts", [])
        out.append(record)
    return out


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> None:
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise RuntimeError("data/tools.json must contain an array")
    tools = normalize(raw)
    if len(tools) < 500:
        raise RuntimeError(f"Only {len(tools)} valid tools in canonical catalog; refusing to publish")
    # Persist normalized records back to the single source of truth.
    write_json(DATA, tools)
    TOOLS.mkdir(exist_ok=True)
    GO.mkdir(exist_ok=True)
    for folder in (TOOLS, GO):
        for child in folder.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
    template = (ROOT / "scripts" / "tool_page.html").read_text(encoding="utf-8")
    for i, tool in enumerate(tools):
        related = [x for x in tools if x["category"] == tool["category"] and x["slug"] != tool["slug"]][:6]
        payload = json.dumps(tool, ensure_ascii=False).replace("</", "<\\/")
        page = template.replace("__TOOL_JSON__", payload).replace("__RELATED_JSON__", json.dumps(related, ensure_ascii=False))
        d = TOOLS / tool["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
        target = html.escape(tool["url"], quote=True)
        redirect = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{target}"><title>Opening {html.escape(tool["title"])}…</title><script>location.replace({json.dumps(tool["url"])})</script></head><body><p>Opening <a href="{target}">{html.escape(tool["title"])} </a>…</p></body></html>'''
        g = GO / tool["slug"]
        g.mkdir(parents=True, exist_ok=True)
        (g / "index.html").write_text(redirect, encoding="utf-8")
    # Homepage/search payload intentionally contains only fields required for discovery.
    compact = [{k: t.get(k) for k in ("title", "slug", "category", "pricing", "logo", "url", "trendingRank")} for t in tools]
    write_json(TOOLS / "index.json", compact)
    print(f"Generated {len(tools)} tools")


if __name__ == "__main__":
    build()
