
const TOOLS_TXT_URL = 'tools.txt'; // relative URL
const OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY_HERE'; // replace with your key

const toolsGrid = document.getElementById('tools-grid');
const categoryFilters = document.getElementById('category-filters');
const searchInput = document.getElementById('search');

let toolsData = [];

async function fetchToolsList() {
  const res = await fetch(TOOLS_TXT_URL);
  const text = await res.text();
  return text.split('\n').map(line => line.trim()).filter(line => line);
}

// Fetch metadata from each URL (title, description, logo)
async function fetchMetaData(url) {
  try {
    const res = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
    const data = await res.json();
    const htmlText = data.contents;

    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, 'text/html');

    const title = doc.querySelector('meta[property="og:title"]')?.content ||
                  doc.querySelector('title')?.innerText || url;

    const description = doc.querySelector('meta[property="og:description"]')?.content ||
                        doc.querySelector('meta[name="description"]')?.content || '';

    const logo = doc.querySelector('meta[property="og:image"]')?.content || '';

    return { url, title, description, logo };

  } catch (e) {
    console.error('Error fetching meta for', url, e);
    return { url, title: url, description: '', logo: '' };
  }
}

// Call OpenAI to enrich data (category, free/paid)
async function enrichWithOpenAI(tool) {
  if (!OPENAI_API_KEY) return tool;

  const prompt = `Categorize this AI tool and mention if it is free, paid, or freemium:
Title: ${tool.title}
Description: ${tool.description}
URL: ${tool.url}
Provide category and pricing status in JSON format like {"category":"", "pricing":""}`;

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

  const json = await response.json();
  try {
    const content = json.choices[0].message.content;
    const parsed = JSON.parse(content);
    return { ...tool, ...parsed };
  } catch {
    return tool;
  }
}

// Render tools in grid
function renderTools(tools) {
  toolsGrid.innerHTML = '';
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

// Initialize app
async function init() {
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
}

// Simple inline search
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

// Build category filters dynamically
function setupCategoryFilters() {
  const categories = [...new Set(toolsData.map(t => t.category).filter(Boolean))];
  if (!categories.length) return;

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
    categoryFilters.appendChild(btn);
  });
}

function setActiveButton(activeBtn) {
  [...categoryFilters.children].forEach(btn => btn.classList.remove('active'));
  activeBtn.classList.add('active');
}

window.onload = init;
