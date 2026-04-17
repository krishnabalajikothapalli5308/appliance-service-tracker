/**
 * Appliance Service Tracker – Technician Portal JS
 * Author: Kothapalli Krishna Balaji
 */

function badge(value) {
  return `<span class="badge badge-${value}">${value.replace('_', ' ')}</span>`;
}

function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast show ${type}`;
  setTimeout(() => { t.className = 'toast'; }, 3000);
}

function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
function closeModalOnOverlay(e, id) { if (e.target.id === id) closeModal(id); }

function updateClock() {
  const el = document.getElementById('topbar-time');
  if (el) el.textContent = new Date().toLocaleString();
}
setInterval(updateClock, 1000);
updateClock();

async function apiFetch(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (!res.ok) { const err = await res.json(); throw new Error(err.error || 'Request failed'); }
  return res.json();
}

// Load technicians into dropdown
async function initTechnicianDropdown() {
  const technicians = await apiFetch('/api/technicians');
  const sel = document.getElementById('tech-filter');
  sel.innerHTML = '<option value="">Select Technician...</option>' +
    technicians.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
}

// Load jobs for selected technician
async function loadTechJobs() {
  const techId = document.getElementById('tech-filter').value;
  const statusFilter = document.getElementById('status-filter').value;
  const tbody = document.getElementById('tech-table');

  if (!techId) {
    tbody.innerHTML = '<tr><td colspan="8" class="loading">Select a technician above to view jobs</td></tr>';
    return;
  }

  const url = statusFilter
    ? `/api/service-requests?status=${statusFilter}`
    : '/api/service-requests';

  const all = await apiFetch(url);
  const jobs = all.filter(r => r.technician_id == techId);

  if (jobs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="loading">No jobs assigned to this technician.</td></tr>';
    return;
  }

  tbody.innerHTML = jobs.map(r => `
    <tr>
      <td><span style="font-family:'Space Mono',monospace;font-size:12px">#${r.id}</span></td>
      <td><strong>${r.appliance_name || '—'}</strong></td>
      <td style="font-size:12px;color:#5a6278">${r.appliance_model || '—'}</td>
      <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${r.issue_description}</td>
      <td>${badge(r.priority)}</td>
      <td>${badge(r.status)}</td>
      <td style="font-size:12px;color:#5a6278">${r.notes || '—'}</td>
      <td>
        <button class="btn btn-sm btn-assign" onclick="openUpdate(${r.id}, '${r.status}', \`${r.notes || ''}\`)">Update</button>
      </td>
    </tr>
  `).join('');
}

function openUpdate(reqId, status, notes) {
  document.getElementById('update-req-id').value = reqId;
  document.getElementById('update-status').value = status;
  document.getElementById('update-notes').value = notes;
  openModal('modal-update');
}

async function submitUpdate() {
  const id = document.getElementById('update-req-id').value;
  const status = document.getElementById('update-status').value;
  const notes = document.getElementById('update-notes').value;
  try {
    await apiFetch(`/api/service-requests/${id}`, 'PUT', { status, notes });
    closeModal('modal-update');
    showToast('Job updated!', 'success');
    loadTechJobs();
  } catch (e) { showToast(e.message, 'error'); }
}

initTechnicianDropdown();
