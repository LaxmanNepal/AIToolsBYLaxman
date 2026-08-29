#!/usr/bin/env python3
"""Single production build entrypoint for the AI tools directory."""
from __future__ import annotations
import json
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tools.json"
TOOLS = ROOT / "tools"
GO = ROOT / "go"
BASE_URL = "https://ai.laxmannepal.com.np"


def compact_index(tools: list[dict]) -> None:
    fields = ("title", "slug", "url", "logo", "category", "pricing", "description", "useCases")
    compact = [{k: t.get(k) for k in fields if t.get(k) is not None} for t in tools]
    (TOOLS / "index.json").write_text(json.dumps(compact, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def build_categories(tools: list[dict]) -> None:
    counts: dict[str, int] = {}
    for tool in tools:
        category = str(tool.get("category") or "AI Tools").strip()
        counts[category] = counts.get(category, 0) + 1
    categories = [{"name": name, "slug": slugify(name), "count": count} for name, count in sorted(counts.items(), key=lambda x: (-x[1], x[0].lower()))]
    (ROOT / "data" / "categories.json").write_text(json.dumps(categories, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    import re
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", value.lower().strip())) or "tool"


def build_seo(tools: list[dict]) -> None:
    lines = ["User-agent: *", "Allow: /", "Disallow: /go/", "", f"Sitemap: {BASE_URL}/sitemap.xml", ""]
    (ROOT / "robots.txt").write_text("\n".join(lines), encoding="utf-8")
    urls = [BASE_URL + "/", BASE_URL + "/github/", BASE_URL + "/trending/"]
    urls += [f"{BASE_URL}/tools/{quote(str(t['slug']))}/" for t in tools if t.get("slug")]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{u}</loc></url>" for u in urls]
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import generate_tools
    generate_tools.build()
    tools = json.loads(DATA.read_text(encoding="utf-8"))
    if len(tools) < 500:
        raise SystemExit(f"Build produced only {len(tools)} tools")
    compact_index(tools)
    build_categories(tools)
    build_seo(tools)
    print(f"Production build complete: {len(tools)} tools")


if __name__ == "__main__":
    main()
