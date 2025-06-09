const TOOLS_TXT_URL = 'https://raw.githubusercontent.com/LaxmanNepal/AIToolsBYLaxman/refs/heads/main/ToolList.txt';

// WARNING: Never commit your real API key publicly!
const OPENAI_API_KEY = 'sk-REPLACE_WITH_YOUR_OWN_KEY'; // <-- Replace this with your actual API key locally

const toolsGrid = document.getElementById('tools-grid');
const categoryFilters = document.getElementById('category-filters');
const searchInput = document.getElementById('search');

let toolsData = [];

async function fetchToolsList() {
  const res = await fetch(TOOLS_TXT_URL);
  if(!res.ok) throw new Error('Failed to fetch tools list');
  const text = await res.text();
  return text.split('\n').map(line => line.trim()).filter(line => line);
}

async function fetchMetaData(url) {
  try {
    const res = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
    if(!res.ok) throw new Error('Failed to fetch page for ' + url);
    const data = await res.json();
    const parser = new DOMParser();
    const doc = parser.parseFromString(data.contents, 'text/html');

    const title = doc.querySelector('meta[property="og:title"]')?.content ||
                  doc.querySelector('title')?.innerText || url;

    const description = doc.querySelector('meta[property="og:description"]')?.content ||
                        doc.querySelector('meta[name="description"]')?.content || '';

    const logo = doc.querySelector('meta[property="og:image"]')?.content || '';

    return { url, title, description, logo };

  } catch (e) {
    console.error('Meta fetch error for', url, e);
    return { url, title: url, description: '', logo: '' };
  }
}

async function enrichWithOpenAI(tool) {
  if (!OPENAI_API_KEY || OPENAI_API_KEY.startsWith('sk-REPLACE')) return tool;

  const prompt = `Categorize this AI tool and mention if it is free, paid, or freemium:
Title: ${tool.title}
Description: ${tool.description}
URL: ${tool.url}
Provide category and pricing status in JSON format like {"category":"", "pricing":""}`;

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 50,
        temperature: 0.3
      })
    });

    if (!response.ok) throw new Error('OpenAI API error');

    const json = await response.json();
    const content = json.choices?.[0]?.message?.content || '{}';

    const parsed = JSON.parse(content);
    return { ...tool, ...parsed };
  } catch (err) {
    console.error('OpenAI enrichment error:', err);
    return tool;
  }
}

function renderTools(tools) {
  toolsGrid.innerHTML = '';
  if (tools.length === 0) {
    toolsGrid.innerHTML = '<p>No tools found matching your search/filter.</p>';
    return;
  }
  tools.forEach(tool => {
    const card = document.createElement('div');
    card.className = 'tool-card';

    card.innerHTML = `
      <img src="${tool.logo || 'assets/default-logo.png'}" alt="${tool.title}" loading="lazy"/>
      <h3>${tool.title}</h3>
      <p>${tool.description}</p>
      <p><b>Category:</b> ${tool.category || 'N/A'}</p>
      <p><b>Pricing:</b> ${tool.pricing || 'Unknown'}</p>
      <a href="${tool.url}" target="_blank" rel="noopener noreferrer" class="btn">Open Tool</a>
    `;

    toolsGrid.appendChild(card);
  });
}

async function init() {
  try {
    const urls = await fetchToolsList();
    let tools = [];
    for (const url of urls) {
      let meta = await fetchMetaData(url);
      meta = await enrichWithOpenAI(meta);
      tools.push(meta);
    }
    toolsData = tools;
    renderTools(toolsData);
    setupSearch();
    setupCategoryFilters();
  } catch (e) {
    toolsGrid.innerHTML = '<p>Error loading tools data.</p>';
    console.error(e);
  }
}

function setupSearch() {
  searchInput.addEventListener('input', () => {
    const q = searchInput.value.toLowerCase();
    const filtered = toolsData.filter(t =>
      t.title.toLowerCase().includes(q) ||
      (t.description && t.description.toLowerCase().includes(q)) ||
      (t.category && t.category.toLowerCase().includes(q))
    );
    renderTools(filtered);
  });
}

function setupCategoryFilters() {
  const categories = [...new Set(toolsData.map(t => t.category).filter(Boolean))];
  if (!categories.length) return;

  categoryFilters.innerHTML = '';

  const btnAll = document.createElement('button');
  btnAll.textContent = 'All';
  btnAll.className = 'active';
  btnAll.onclick = () => {
    renderTools(toolsData);
    setActiveButton(btnAll);
  };
  categoryFilters.appendChild(btnAll);

  categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.textContent = cat;
    btn.onclick = () => {
      const filtered = toolsData.filter(t => t.category === cat);
      renderTools(filtered);
      setActiveButton(btn);
    };
    categoryFilte
