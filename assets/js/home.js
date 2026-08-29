(() => {
  'use strict';
  const DATA_URL = 'data/tools.json';
  const PAGE_SIZE = 48;
  const $ = (s) => document.querySelector(s);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const normalize = (v) => String(v ?? '').toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const favorites = () => new Set(JSON.parse(localStorage.getItem('ai-tools-favorites') || '[]'));
  const saveFavorites = (set) => localStorage.setItem('ai-tools-favorites', JSON.stringify([...set]));
  let tools = [], filtered = [], category = 'all', page = 1, favoritesOnly = false;

  function searchMatch(tool, query) {
    if (!query) return true;
    const q = normalize(query);
    const hay = normalize([tool.title, tool.category, tool.pricing, tool.description, ...(tool.tags || []), ...(tool.useCases || [])].join(' '));
    return hay.includes(q) || normalize(tool.title).split(' ').some(word => word.startsWith(q));
  }

  function apply() {
    const query = $('#catalog-search').value.trim();
    const pricing = $('#pricing').value;
    filtered = tools.filter(t =>
      (category === 'all' || t.category === category) &&
      (!favoritesOnly || favorites().has(t.slug)) &&
      (pricing === 'all' || normalize(t.pricing) === normalize(pricing)) &&
      searchMatch(t, query)
    );
    const sort = $('#sort').value;
    filtered.sort((a, b) => {
      if (sort === 'name') return String(a.title).localeCompare(String(b.title));
      if (sort === 'new') return String(b.createdAt || b.lastVerified || '').localeCompare(String(a.createdAt || a.lastVerified || ''));
      if (sort === 'free') return pricingRank(a.pricing) - pricingRank(b.pricing) || String(a.title).localeCompare(String(b.title));
      return Number(a.trendingRank || 999999) - Number(b.trendingRank || 999999);
    });
    render();
  }
  function pricingRank(v) { const x = normalize(v); return x === 'free' ? 0 : x === 'freemium' ? 1 : x === 'paid' ? 2 : 3; }
  function render() {
    const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    page = Math.min(page, pages);
    const start = (page - 1) * PAGE_SIZE;
    const visible = filtered.slice(start, start + PAGE_SIZE);
    $('#result-count').textContent = `${filtered.length.toLocaleString()} tool${filtered.length === 1 ? '' : 's'} shown`;
    $('#page-info').textContent = `Page ${page} of ${pages}`;
    $('#prev').disabled = page <= 1;
    $('#next').disabled = page >= pages;
    const fav = favorites();
    $('#tools').innerHTML = visible.length ? visible.map(t => `
      <article class="tool-card">
        <a class="tool-link" href="tools/${encodeURIComponent(t.slug)}/">
          <img src="${esc(t.logo || 'icon.svg')}" alt="${esc(t.title)} logo" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='icon.svg'">
          <div class="tool-title">${esc(t.title)}</div>
          <div class="tool-category">${esc(t.category || 'AI Tool')}</div>
          <div class="tool-price">${esc(t.pricing || 'Check provider')}</div>
        </a>
        <div class="tool-actions">
          <button type="button" class="small-btn ${fav.has(t.slug) ? 'selected' : ''}" data-fav="${esc(t.slug)}">${fav.has(t.slug) ? '♥ Saved' : '♡ Save'}</button>
        </div>
      </article>`).join('') : '<div class="empty">No matching AI tools. Try another search or remove a filter.</div>';
    $('#saved-count').textContent = fav.size.toLocaleString();
  }
  function buildCategories() {
    const map = new Map();
    tools.forEach(t => map.set(t.category || 'AI Tools', (map.get(t.category || 'AI Tools') || 0) + 1));
    $('#filters').innerHTML = `<button type="button" class="filter active" data-category="all">All (${tools.length})</button>` +
      [...map.entries()].sort((a,b) => b[1] - a[1]).map(([name,count]) => `<button type="button" class="filter" data-category="${esc(name)}">${esc(name.replace(/^AI\s+/i,''))} (${count})</button>`).join('');
  }
  function bind() {
    $('#catalog-search').addEventListener('input', () => { page = 1; clearTimeout(bind.timer); bind.timer = setTimeout(apply, 120); });
    $('#pricing').addEventListener('change', () => { page = 1; apply(); });
    $('#sort').addEventListener('change', () => { page = 1; apply(); });
    $('#favorites-only').addEventListener('click', (e) => { favoritesOnly = !favoritesOnly; e.currentTarget.classList.toggle('active', favoritesOnly); page = 1; apply(); });
    $('#filters').addEventListener('click', (e) => { const btn = e.target.closest('[data-category]'); if (!btn) return; category = btn.dataset.category; page = 1; document.querySelectorAll('.filter').forEach(x => x.classList.toggle('active', x === btn)); apply(); });
    $('#tools').addEventListener('click', (e) => { const btn = e.target.closest('[data-fav]'); if (!btn) return; const set = favorites(); set.has(btn.dataset.fav) ? set.delete(btn.dataset.fav) : set.add(btn.dataset.fav); saveFavorites(set); render(); });
    $('#prev').onclick = () => { if (page > 1) { page--; render(); scrollTo({top: $('#all-tools').offsetTop - 70, behavior:'smooth'}); } };
    $('#next').onclick = () => { const pages = Math.ceil(filtered.length / PAGE_SIZE); if (page < pages) { page++; render(); scrollTo({top: $('#all-tools').offsetTop - 70, behavior:'smooth'}); } };
    $('#search-form').onsubmit = (e) => { e.preventDefault(); const q = $('#catalog-search').value.trim(); if (q) location.href = `search/?q=${encodeURIComponent(q)}`; };
  }
  fetch(DATA_URL, { cache: 'no-cache' }).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }).then(data => {
    if (!Array.isArray(data)) throw new Error('Catalog must be a JSON array');
    tools = data.filter(t => t && t.title && t.slug && t.url);
    $('#total-count').textContent = tools.length.toLocaleString();
    $('#category-count').textContent = new Set(tools.map(t => t.category).filter(Boolean)).size.toLocaleString();
    buildCategories(); bind(); apply();
  }).catch(err => { console.error(err); $('#result-count').textContent = 'Catalog unavailable'; $('#tools').innerHTML = `<div class="empty error">Unable to load <strong>data/tools.json</strong>. ${esc(err.message)}</div>`; });
})();
