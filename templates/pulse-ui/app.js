// Pulse UI v1 — reads .pulse-state.json, renders 5 sections.
// Data contract: see docs/systems/pulse-monitor.md and conventions/26-pulse-monitor.md
// The UI is expirable; the contract is durable. Redesign freely.

const STATE_URL = '.pulse-state.json';

function text(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? '';
}

function statusBadgeClass(status) {
  const s = (status || '').toLowerCase().replace(/[_\s]+/g, '-');
  if (['implemented', 'configured', 'verified'].includes(s)) return 'badge-implemented';
  if (['not-started', 'pending', 'planned'].includes(s)) return 'badge-not-started';
  if (s === 'deferred' || s === 'n-a' || s === 'n/a') return 'badge-deferred';
  return '';
}

function renderTechStack(stack) {
  const dl = document.getElementById('tech-stack');
  dl.innerHTML = '';
  (stack || []).forEach(({ key, value }) => {
    const dt = document.createElement('dt');
    dt.textContent = key;
    const dd = document.createElement('dd');
    dd.textContent = value;
    dl.append(dt, dd);
  });
}

function renderSystems(systems) {
  const container = document.getElementById('systems');
  container.innerHTML = '';
  (systems || []).forEach((s) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-title">
        <span>${s.name}</span>
        <span class="badge ${statusBadgeClass(s.status)}">${s.status || '?'}</span>
      </div>
      <div class="card-meta">
        <span>Convention: ${s.convention || '—'}</span>
        ${s.location ? `<span> · Location: <code>${s.location}</code></span>` : ''}
      </div>
    `;
    container.appendChild(card);
  });
  if (!systems || systems.length === 0) {
    container.innerHTML = '<p class="muted">No foundational systems declared yet.</p>';
  }
}

function renderFeatures(features) {
  const container = document.getElementById('features');
  container.innerHTML = '';
  (features || []).forEach((f) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-title"><span>${f.name}</span></div>
      <div class="card-meta">
        ${f.location ? `Location: <code>${f.location}</code>` : ''}
        ${f.routes ? ` · Routes: <code>${f.routes}</code>` : ''}
      </div>
    `;
    container.appendChild(card);
  });
  if (!features || features.length === 0) {
    container.innerHTML = '<p class="muted">No features declared yet.</p>';
  }
}

async function refresh() {
  try {
    const resp = await fetch(`${STATE_URL}?_=${Date.now()}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    text('project-name', data.project?.name || 'Project Pulse');
    text('project-purpose', data.project?.purpose || '');
    const meta = [data.project?.stage].filter(Boolean).join(' · ');
    text('project-meta', meta);
    renderTechStack(data.techStack);
    renderSystems(data.foundationalSystems);
    renderFeatures(data.features);
    text('architecture', data.architecture || '(no folder structure declared in References.md)');
    text('generated-at', data.generatedAt || '?');
    text('contract-version', data.dataContractVersion || '?');
  } catch (err) {
    text('project-name', 'Pulse — load failed');
    text('project-purpose', `Could not load ${STATE_URL}. Run \`./archetype/scripts/pulse-inspect.sh --out .pulse-state.json\` and refresh.`);
    console.error('Pulse load failed', err);
  }
}

document.getElementById('refresh-btn')?.addEventListener('click', refresh);
refresh();
