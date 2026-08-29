#!/usr/bin/env python3
"""Fail-fast validation for the generated production site."""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", value.lower().strip())) or "tool"


def main() -> None:
    data = ROOT / "data" / "tools.json"
    index = ROOT / "tools" / "index.json"
    assert data.is_file() and data.stat().st_size > 0, "data/tools.json missing"
    assert index.is_file() and index.stat().st_size > 0, "tools/index.json missing"
    tools = json.loads(data.read_text(encoding="utf-8"))
    compact = json.loads(index.read_text(encoding="utf-8"))
    assert isinstance(tools, list) and len(tools) >= 500, f"Expected 500+ tools, found {len(tools)}"
    assert len(compact) == len(tools), "Compact catalog count mismatch"

    slugs: set[str] = set()
    urls: set[str] = set()
    for tool in tools:
        title = str(tool.get("title") or "").strip()
        url = str(tool.get("url") or "").strip()
        slug = str(tool.get("slug") or slugify(title))
        assert title, "Tool title missing"
        assert url and urlparse(url).scheme in {"http", "https"}, f"Invalid URL for {title}"
        assert slug not in slugs, f"Duplicate slug: {slug}"
        assert url.rstrip("/").lower() not in urls, f"Duplicate URL: {url}"
        slugs.add(slug)
        urls.add(url.rstrip("/").lower())
        assert (ROOT / "tools" / slug / "index.html").is_file(), f"Missing detail page: {slug}"
        assert (ROOT / "go" / slug / "index.html").is_file(), f"Missing redirect: {slug}"

    assert (ROOT / "sitemap.xml").is_file(), "sitemap.xml missing"
    assert (ROOT / "robots.txt").is_file(), "robots.txt missing"
    assert "AItools/" not in (ROOT / "index.html").read_text(encoding="utf-8"), "Legacy AItools route remains in homepage"
    assert "fetch('tools/index.json'" in (ROOT / "index.html").read_text(encoding="utf-8"), "Homepage is not using canonical catalog"
    print(f"Validated {len(tools)} tools, {len(slugs)} unique routes and {len(urls)} unique URLs")


if __name__ == "__main__":
    main()
