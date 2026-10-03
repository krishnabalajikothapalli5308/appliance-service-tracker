/**
 * Appliance Service Tracker – Admin Dashboard JS
 * Author: Kothapalli Krishna Balaji
 */

// ── HELPERS ──────────────────────────────────────────────────────────────

function badge(value) {
  const label = value.replace('_', ' ');
  return `<span class="badge badge-${value}">${label}</span>`;
}

function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast show ${type}`;
  setTimeout(() => { t.className = 'toast'; }, 3000);
}

function openModal(id) {
  document.getElementById(id).classList.add('open');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}
function closeModalOnOverlay(e, id) {
  if (e.target.id === id) closeModal(id);
}

function updateClock() {
  const el = document.getElementById('topbar-time');
  if (el) el.textContent = new Date().toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
}
setInterval(updateClock, 1000);
updateClock();

async function apiFetch(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(err.error || 'Request failed');
  }
  return res.json();
}

function initials(name) {
  return name ? name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : '?';
}

// ── NAVIGATION ───────────────────────────────────────────────────────────

const sectionMeta = {
  dashboard: { title: 'Dashboard', badge: 'Overview' },
  appliances: { title: 'Appliances', badge: 'Inventory' },
  'service-requests': { title: 'Service Requests', badge: 'Manage' },
  technicians: { title: 'Technicians', badge: 'Team' }
};

function showSection(name, el) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.getElementById(`section-${name}`).classList.add('active');
  if (el) el.classList.add('active');

  const meta = sectionMeta[name];
  document.getElementById('topbar-title').textContent = meta.title;
  document.getElementById('topbar-badge').textContent = meta.badge;

  if (name === 'dashboard') loadDashboard();
  if (name === 'appliances') loadAppliances();
  if (name === 'service-requests') loadServiceRequests();
  if (name === 'technicians') loadTechnicians();
}

// ── DASHBOARD ────────────────────────────────────────────────────────────

async function loadDashboard() {
  try {
    const stats = await apiFetch('/api/stats');
    document.getElementById('stat-appliances').textContent  = stats.total_appliances;
    document.getElementById('stat-open').textContent        = stats.open_requests;
    document.getElementById('stat-inprogress').textContent  = stats.in_progress;
    document.getElementById('stat-completed').textContent   = stats.completed;
    document.getElementById('stat-technicians').textContent = stats.total_technicians;

    const requests = await apiFetch('/api/service-requests');
    const recent = requests.slice(0, 8);
    document.getElementById('dash-count').textContent = `${recent.length} recent`;

    const tbody = document.getElementById('dashboard-table');
    if (recent.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="loading">No service requests yet.</td></tr>';
      return;
    }
    tbody.innerHTML = recent.map(r => `
      <tr>
        <td class="td-id">#${r.id}</td>
        <td class="td-name">${r.appliance_name || '—'}</td>
        <td class="td-truncate td-soft">${r.issue_description}</td>
        <td>${badge(r.priority)}</td>
        <td>${badge(r.status)}</td>
        <td class="td-soft">${r.created_at || '—'}</td>
      </tr>
    `).join('');
  } catch (e) { showToast(e.message, 'error'); }
}

// ── APPLIANCES ───────────────────────────────────────────────────────────

async function loadAppliances() {
  try {
    const appliances = await apiFetch('/api/appliances');
    const tbody = document.getElementById('appliances-table');
    if (appliances.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="loading">No appliances found.</td></tr>';
      return;
    }
    tbody.innerHTML = appliances.map(a => `
      <tr>
        <td class="td-id">${a.id}</td>
        <td class="td-name">${a.name}</td>
        <td class="td-soft">${a.model}</td>
        <td class="td-soft">${a.serial_number || '—'}</td>
        <td class="td-soft">${a.location || '—'}</td>
        <td>${badge(a.status)}</td>
        <td class="td-id" style="text-align:center">${a.total_service_requests}</td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="deleteAppliance(${a.id})">Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (e) { showToast(e.message, 'error'); }
}

async function submitAddAppliance() {
  const name  = document.getElementById('a-name').value.trim();
  const model = document.getElementById('a-model').value.trim();
  if (!name || !model) { showToast('Name and Model are required', 'error'); return; }
  try {
    await apiFetch('/api/appliances', 'POST', {
      name, model,
      serial_number: document.getElementById('a-serial').value.trim() || null,
      location: document.getElementById('a-location').value.trim(),
      purchase_date: document.getElementById('a-date').value
    });
    closeModal('modal-add-appliance');
    showToast('Appliance added successfully', 'success');
    loadAppliances();
    ['a-name','a-model','a-serial','a-location','a-date'].forEach(id => document.getElementById(id).value = '');
  } catch (e) { showToast(e.message, 'error'); }
}

async function deleteAppliance(id) {
  if (!confirm('Delete this appliance and all its service requests?')) return;
  try {
    await apiFetch(`/api/appliances/${id}`, 'DELETE');
    showToast('Appliance deleted', 'success');
    loadAppliances();
  } catch (e) { showToast(e.message, 'error'); }
}

// ── SERVICE REQUESTS ─────────────────────────────────────────────────────

async function loadServiceRequests() {
  try {
    const status = document.getElementById('filter-status').value;
    const url = status ? `/api/service-requests?status=${status}` : '/api/service-requests';
    const requests = await apiFetch(url);
    const tbody = document.getElementById('requests-table');
    if (requests.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="loading">No requests found.</td></tr>';
      return;
    }
    tbody.innerHTML = requests.map(r => `
      <tr>
        <td class="td-id">#${r.id}</td>
        <td class="td-name">${r.appliance_name || '—'}</td>
        <td class="td-truncate td-soft">${r.issue_description}</td>
        <td>${badge(r.priority)}</td>
        <td>${badge(r.status)}</td>
        <td class="td-soft">${r.technician_name || '<span style="color:#cbd5e1">Unassigned</span>'}</td>
        <td class="td-soft">${r.created_at || '—'}</td>
        <td style="display:flex;gap:6px">
          <button class="btn btn-sm btn-edit" onclick="openAssign(${r.id},${r.technician_id||'null'},'${r.status}',\`${(r.notes||'').replace(/`/g,"'")}\`)">Edit</button>
          <button class="btn btn-sm btn-danger" onclick="deleteRequest(${r.id})">Del</button>
        </td>
      </tr>
    `).join('');
  } catch (e) { showToast(e.message, 'error'); }
}

async function submitAddRequest() {
  const applianceId = document.getElementById('r-appliance').value;
  const issue = document.getElementById('r-issue').value.trim();
  if (!applianceId || !issue) { showToast('Appliance and issue are required', 'error'); return; }
  try {
    await apiFetch('/api/service-requests', 'POST', {
      appliance_id: parseInt(applianceId),
      issue_description: issue,
      priority: document.getElementById('r-priority').value
    });
    closeModal('modal-add-request');
    showToast('Service request submitted', 'success');
    loadServiceRequests();
    document.getElementById('r-issue').value = '';
  } catch (e) { showToast(e.message, 'error'); }
}

async function deleteRequest(id) {
  if (!confirm('Delete this service request?')) return;
  try {
    await apiFetch(`/api/service-requests/${id}`, 'DELETE');
    showToast('Request deleted', 'success');
    loadServiceRequests();
  } catch (e) { showToast(e.message, 'error'); }
}

async function openAssign(reqId, techId, status, notes) {
  const technicians = await apiFetch('/api/technicians');
  const sel = document.getElementById('assign-tech');
  sel.innerHTML = '<option value="">— Unassigned —</option>' +
    technicians.map(t => `<option value="${t.id}" ${t.id == techId ? 'selected' : ''}>${t.name} · ${t.specialization}</option>`).join('');
  document.getElementById('assign-status').value = status;
  document.getElementById('assign-notes').value = notes;
  document.getElementById('assign-req-id').value = reqId;
  openModal('modal-assign');
}

async function submitAssign() {
  const id     = document.getElementById('assign-req-id').value;
  const techId = document.getElementById('assign-tech').value;
  const status = document.getElementById('assign-status').value;
  const notes  = document.getElementById('assign-notes').value;
  try {
    await apiFetch(`/api/service-requests/${id}`, 'PUT', {
      technician_id: techId ? parseInt(techId) : null,
      status, notes
    });
    closeModal('modal-assign');
    showToast('Request updated', 'success');
    loadServiceRequests();
  } catch (e) { showToast(e.message, 'error'); }
}

// ── TECHNICIANS ───────────────────────────────────────────────────────────

async function loadTechnicians() {
  try {
    const technicians = await apiFetch('/api/technicians');
    const grid = document.getElementById('technician-grid');
    if (technicians.length === 0) {
      grid.innerHTML = '<div class="loading">No technicians found.</div>';
      return;
    }
    grid.innerHTML = technicians.map(t => `
      <div class="tech-card">
        <div class="tech-card-top">
          <div>
            <div class="tech-name">${t.name}</div>
            <div class="tech-spec">${t.specialization}</div>
          </div>
          <div class="tech-avatar">${initials(t.name)}</div>
        </div>
        <div class="tech-meta">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.6 3.39a2 2 0 0 1 1.94-2.19h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.78a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
          </svg>
          ${t.contact || '—'}
          &nbsp;·&nbsp; <strong>${t.total_assigned}</strong> jobs
          &nbsp;·&nbsp; <span class="tech-avail ${t.available ? 'yes' : 'no'}">${t.available ? '● Available' : '● Busy'}</span>
        </div>
      </div>
    `).join('');
  } catch (e) { showToast(e.message, 'error'); }
}

async function submitAddTechnician() {
  const name = document.getElementById('t-name').value.trim();
  const spec  = document.getElementById('t-spec').value.trim();
  if (!name || !spec) { showToast('Name and specialization required', 'error'); return; }
  try {
    await apiFetch('/api/technicians', 'POST', {
      name, specialization: spec,
      contact: document.getElementById('t-contact').value.trim()
    });
    closeModal('modal-add-technician');
    showToast('Technician added', 'success');
    loadTechnicians();
    ['t-name','t-spec','t-contact'].forEach(id => document.getElementById(id).value = '');
  } catch (e) { showToast(e.message, 'error'); }
}

// ── POPULATE ADD REQUEST MODAL ─────────────────────────────────────────────

window.openModal = async function(id) {
  document.getElementById(id).classList.add('open');
  if (id === 'modal-add-request') {
    const appliances = await apiFetch('/api/appliances');
    const sel = document.getElementById('r-appliance');
    sel.innerHTML = '<option value="">Select appliance...</option>' +
      appliances.map(a => `<option value="${a.id}">${a.name} – ${a.model}</option>`).join('');
  }
};

// ── INIT ──────────────────────────────────────────────────────────────────
loadDashboard();
