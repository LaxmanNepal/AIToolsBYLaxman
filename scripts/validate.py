#!/usr/bin/env python3
"""Fail-fast validation for the generated production site."""
from __future__ import annotations
import json, re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("title", "slug", "url", "category", "pricing", "description", "lastVerified")


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
    assert len(compact) == len(tools), "Discovery index count mismatch"
    assert len(index.read_bytes()) < len(data.read_bytes()), "Discovery index is not smaller than canonical data"
    slugs: set[str] = set(); urls: set[str] = set(); categories: set[str] = set()
    for tool in tools:
        missing = [k for k in REQUIRED if not str(tool.get(k) or "").strip()]
        assert not missing, f"Missing fields {missing} for {tool.get('title')}"
        title, url, slug = str(tool["title"]).strip(), str(tool["url"]).strip(), str(tool["slug"]).strip()
        parsed = urlparse(url)
        assert parsed.scheme in {"http", "https"} and parsed.netloc, f"Invalid URL for {title}"
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), f"Invalid slug: {slug}"
        assert slug not in slugs, f"Duplicate slug: {slug}"
        assert url.rstrip("/").lower() not in urls, f"Duplicate URL: {url}"
        assert len(str(tool["description"])) <= 500, f"Description too long: {title}"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(tool["lastVerified"])), f"Invalid lastVerified: {title}"
        categories.add(str(tool["category"]).strip()); slugs.add(slug); urls.add(url.rstrip("/").lower())
        assert (ROOT / "tools" / slug / "index.html").is_file(), f"Missing detail page: {slug}"
        assert (ROOT / "go" / slug / "index.html").is_file(), f"Missing redirect: {slug}"
    assert (ROOT / "sitemap.xml").is_file(), "sitemap.xml missing"
    assert (ROOT / "robots.txt").is_file(), "robots.txt missing"
    assert not (ROOT / "AItools").exists(), "Legacy AItools directory remains"
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "AItools/" not in homepage, "Legacy AItools route remains in homepage"
    assert "tools/index.json" in homepage, "Homepage is not using canonical discovery index"
    assert "OPENAI_API_KEY" not in homepage and "api.openai.com" not in homepage, "Secret/API architecture leaked into frontend"
    assert not (ROOT / "everything.json").exists(), "Duplicate everything.json remains"
    assert not (ROOT / "ToolList.txt").exists(), "Obsolete ToolList.txt remains"
    print(f"Validated {len(tools)} tools, {len(categories)} categories, {len(slugs)} routes and {len(urls)} unique URLs")


if __name__ == "__main__": main()
