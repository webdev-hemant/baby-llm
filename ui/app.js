/**
 * Baby LLM: Glass-Box Frontend Engine & Telemetry Controller
 * Precision Engineering Architecture (Zero AI Slop)
 */

const API_BASE = window.location.origin.startsWith("http")
  ? window.location.origin
  : "http://127.0.0.1:21225";

// Application State
let activeMemories = [];
let activeCategory = "all";
let searchQuery = "";
let currentSort = "recent";
let activeCommitments = [];

// DOM References
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const memoryCardsContainer = document.getElementById("memory-cards-container");
const memoryCount = document.getElementById("memory-count");
const tabVaultCounter = document.getElementById("tab-vault-counter");
const morningBriefText = document.getElementById("morning-brief-text");
const commitmentsList = document.getElementById("commitments-list");
const commitmentsCounter = document.getElementById("commitments-counter");
const timelineList = document.getElementById("timeline-list");
const btnTriggerDream = document.getElementById("btn-trigger-dream");
const btnDreamLabel = document.getElementById("btn-dream-label");
const modalAddMemory = document.getElementById("modal-add-memory");
const btnAddMemory = document.getElementById("btn-add-memory");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelMemory = document.getElementById("btn-cancel-memory");
const formCreateMemory = document.getElementById("form-create-memory");
const toggleIncognito = document.getElementById("toggle-incognito");
const incognitoPillText = document.getElementById("incognito-pill-text");
const toastDock = document.getElementById("toast-dock");
const vaultSearchInput = document.getElementById("vault-search-input");
const btnClearSearch = document.getElementById("btn-clear-search");
const vaultSortSelect = document.getElementById("vault-sort-select");
const formQuickGoal = document.getElementById("form-quick-goal");
const inputQuickGoal = document.getElementById("input-quick-goal");
const btnRefreshBrief = document.getElementById("btn-refresh-brief");
const modalReflection = document.getElementById("modal-reflection");
const btnOpenReflection = document.getElementById("btn-open-reflection");
const btnCloseReflection = document.getElementById("btn-close-reflection");
const btnCancelReflection = document.getElementById("btn-cancel-reflection");
const formReflection = document.getElementById("form-reflection");
const reflectionInput = document.getElementById("reflection-input");
const reflectionResponseBox = document.getElementById("reflection-response-box");
const reflectionResponseText = document.getElementById("reflection-response-text");

// Category importance weights (matches decay.py)
const CATEGORY_WEIGHTS = {
  health: 3.0,
  finance: 3.0,
  goal: 2.5,
  work: 2.0,
  relationship: 2.0,
  lifestyle: 1.2,
  preference: 1.0,
};

// ==========================================================================
// Toast Notification Engine
// ==========================================================================
function showToast(message, type = "info", duration = 3500) {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span class="toast-msg">${escapeHtml(message)}</span>`;
  toastDock.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "all 0.25s ease";
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// ==========================================================================
// Tab Switching
// ==========================================================================
document.querySelectorAll(".stage-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".stage-tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));

    tab.classList.add("active");
    const targetId = tab.dataset.tab;
    const targetPanel = document.getElementById(targetId);
    if (targetPanel) targetPanel.classList.add("active");

    if (targetId === "view-mindstream") {
      loadMemories();
    } else if (targetId === "view-timeline") {
      renderTimeline();
    } else if (targetId === "view-telemetry") {
      updateTelemetry();
    }
  });
});

// ==========================================================================
// Incognito Toggle
// ==========================================================================
if (toggleIncognito) {
  toggleIncognito.addEventListener("change", () => {
    if (toggleIncognito.checked) {
      if (incognitoPillText) incognitoPillText.textContent = "Incognito: ON (Unlogged)";
      if (chatInput) chatInput.placeholder = "Incognito Mode: WAL logging bypassed for this query...";
      showToast("Incognito Mode Active: Query will not be written to memory.", "warning");
    } else {
      if (incognitoPillText) incognitoPillText.textContent = "Incognito: Off";
      if (chatInput) chatInput.placeholder = "Ask a question, update a belief, or record a life update...";
    }
  });
}

// Auto-expand textarea on typing & handle Return key
if (chatInput) {
  chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });
}

// Starter Prompts Click
document.querySelectorAll(".prompt-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    const text = chip.dataset.text;
    if (text && chatInput) {
      chatInput.value = text;
      chatForm.dispatchEvent(new Event("submit"));
    }
  });
});

// ==========================================================================
// Chat Submission & Rendering
// ==========================================================================
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  const startTime = performance.now();
  appendMessage(text, "user");
  chatInput.value = "";
  chatInput.style.height = "auto";

  const placeholderId = appendMessage("Assembling bi-temporal context & running local inference...", "assistant", true);
  const isIncognito = toggleIncognito && toggleIncognito.checked;

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, incognito: isIncognito }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const duration = Math.round(performance.now() - startTime);

    updateMessage(placeholderId, data.reply, {
      duration,
      incognito: data.incognito,
      probed: data.probed,
    });

    // Refresh memory count in background
    loadMemories(true);
  } catch (err) {
    updateMessage(
      placeholderId,
      `⚠️ **Connection Notice:** Unable to reach Baby LLM server at \`${API_BASE}\`. Ensure \`baby-llm ui\` is running.`,
      { error: true }
    );
  }
});

function appendMessage(text, sender, isPlaceholder = false) {
  const id = "msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 4);
  const row = document.createElement("div");
  row.className = `chat-row ${sender}-row`;
  row.id = id;

  const isUser = sender === "user";
  const avatarHtml = isUser
    ? `<div class="user-avatar">You</div>`
    : `<div class="bot-avatar"><img src="icon.svg" width="18" height="18" alt="Baby LLM"></div>`;

  row.innerHTML = `
    <div class="avatar-cell">${avatarHtml}</div>
    <div class="bubble-cell">
      <div class="bubble-header">
        <span class="author-label">${isUser ? "You" : "Baby LLM"}</span>
        <span class="bubble-meta">${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
      </div>
      <div class="bubble-body">
        <p>${formatMarkdown(text)}</p>
      </div>
    </div>
  `;

  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function updateMessage(id, newText, meta = {}) {
  const row = document.getElementById(id);
  if (!row) return;

  const bubbleBody = row.querySelector(".bubble-body");
  const bubbleMeta = row.querySelector(".bubble-meta");

  if (bubbleBody) {
    bubbleBody.innerHTML = `<p>${formatMarkdown(newText)}</p>`;
  }

  if (bubbleMeta && meta.duration) {
    const incogBadge = meta.incognito ? " · Incognito" : "";
    bubbleMeta.textContent = `${meta.duration}ms${incogBadge}`;
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ==========================================================================
// Mindstream Vault (Memories)
// ==========================================================================
async function loadMemories(silent = false) {
  try {
    const res = await fetch(`${API_BASE}/api/memories?active_only=false`);
    if (res.ok) {
      activeMemories = await res.json();
      const activeCount = activeMemories.filter(m => m.is_active).length;
      if (memoryCount) memoryCount.textContent = activeCount;
      if (tabVaultCounter) tabVaultCounter.textContent = activeCount;

      renderMemoryCards();
      updateTelemetry();
    }
  } catch (err) {
    if (!silent) console.warn("Failed to load memories:", err);
  }
}

function calculateRetention(node) {
  if (node.ymyl_protected) return 1.0;
  const now = new Date();
  const lastReinforced = new Date(node.last_reinforced_at || node.valid_from || now);
  const elapsedDays = Math.max(0, (now - lastReinforced) / (1000 * 86400));
  const importance = CATEGORY_WEIGHTS[node.category.toLowerCase()] || 1.0;
  const stability = Math.max(0.1, node.stability || 1.0);
  const exponent = -elapsedDays / (stability * importance);
  return Math.min(1.0, Math.max(0.0, Math.exp(exponent)));
}

function renderMemoryCards() {
  if (!memoryCardsContainer) return;
  memoryCardsContainer.innerHTML = "";

  let list = activeMemories.filter(m => {
    if (!m.is_active) return false;
    if (activeCategory !== "all" && m.category.toLowerCase() !== activeCategory.toLowerCase()) {
      return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchFact = m.fact && m.fact.toLowerCase().includes(q);
      const matchSubj = m.subject && m.subject.toLowerCase().includes(q);
      const matchObj = m.object && m.object.toLowerCase().includes(q);
      const matchPred = m.predicate && m.predicate.toLowerCase().includes(q);
      if (!matchFact && !matchSubj && !matchObj && !matchPred) return false;
    }
    return true;
  });

  // Sort
  if (currentSort === "stability") {
    list.sort((a, b) => (b.stability || 0) - (a.stability || 0));
  } else if (currentSort === "confidence") {
    list.sort((a, b) => (b.confidence || 0) - (a.confidence || 0));
  } else {
    // recent
    list.sort((a, b) => new Date(b.valid_from) - new Date(a.valid_from));
  }

  if (list.length === 0) {
    memoryCardsContainer.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px 0; color: var(--text-muted);">
        <p style="font-size: 13px;">No memory nodes match the current filter.</p>
        <p style="font-size: 11.5px; margin-top: 4px;">Chat with Baby LLM or click <strong>+ Add Fact</strong> above.</p>
      </div>
    `;
    return;
  }

  list.forEach(m => {
    const card = document.createElement("div");
    card.className = "vault-card";

    const retention = calculateRetention(m);
    const retentionPct = Math.round(retention * 100);
    const gaugeColor = retention >= 0.7 ? "var(--color-emerald)" : (retention >= 0.4 ? "var(--color-amber)" : "var(--color-rose)");
    const ymylBadge = m.ymyl_protected
      ? `<span class="ymyl-badge-flag" title="Infinite retention floor"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> YMYL</span>`
      : "";

    const validDate = new Date(m.valid_from).toLocaleDateString([], { month: "short", day: "numeric" });

    card.innerHTML = `
      <div>
        <div class="card-top-row">
          <span class="badge-tag ${m.category.toLowerCase()}">${m.category}</span>
          ${ymylBadge}
        </div>
        <div class="card-fact-text">${escapeHtml(m.fact)}</div>
        <div class="spo-breakdown">
          <span class="spo-token">${escapeHtml(m.subject)}</span>
          <span class="spo-token pred">${escapeHtml(m.predicate)}</span>
          <span class="spo-token">${escapeHtml(m.object)}</span>
        </div>
      </div>
      <div>
        <div class="card-gauge-row">
          <div class="gauge-labels">
            <span>Retention ${m.ymyl_protected ? 'Floor' : ''}</span>
            <span>${retentionPct}% · Stab: ${(m.stability || 1).toFixed(1)}d</span>
          </div>
          <div class="gauge-track">
            <div class="gauge-fill" style="width: ${retentionPct}%; background-color: ${gaugeColor};"></div>
          </div>
        </div>
        <div class="card-actions-bar">
          <span class="card-timestamp">${validDate}</span>
          <div class="card-buttons">
            <button class="mini-action-btn" onclick="openEditMemory('${m.id}')" title="Edit fact">Edit</button>
            <button class="mini-action-btn danger" onclick="eraseMemory('${m.id}')" title="Permanently delete">Erase</button>
          </div>
        </div>
      </div>
    `;

    memoryCardsContainer.appendChild(card);
  });
}

// Category filter clicks
document.querySelectorAll(".filter-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    activeCategory = pill.dataset.category;
    renderMemoryCards();
  });
});

// Search input
if (vaultSearchInput) {
  vaultSearchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value.trim();
    if (btnClearSearch) btnClearSearch.style.display = searchQuery ? "block" : "none";
    renderMemoryCards();
  });
}

if (btnClearSearch) {
  btnClearSearch.addEventListener("click", () => {
    vaultSearchInput.value = "";
    searchQuery = "";
    btnClearSearch.style.display = "none";
    renderMemoryCards();
  });
}

if (vaultSortSelect) {
  vaultSortSelect.addEventListener("change", (e) => {
    currentSort = e.target.value;
    renderMemoryCards();
  });
}

// One-click Erase Memory Node
window.eraseMemory = async function(id) {
  const node = activeMemories.find(m => m.id === id);
  const factName = node ? node.fact : "this memory";
  if (!confirm(`Erase fact permanently?\n\n"${factName}"`)) return;

  try {
    const res = await fetch(`${API_BASE}/api/memories/${id}`, { method: "DELETE" });
    if (res.ok) {
      activeMemories = activeMemories.filter(m => m.id !== id);
      renderMemoryCards();
      renderTimeline();
      updateTelemetry();
      const count = activeMemories.filter(m => m.is_active).length;
      if (memoryCount) memoryCount.textContent = count;
      if (tabVaultCounter) tabVaultCounter.textContent = count;
      showToast("Memory node permanently erased from SQLite & LanceDB.", "info");
    } else {
      showToast("Could not erase node from server.", "error");
    }
  } catch (err) {
    showToast("Error erasing memory: " + err.message, "error");
  }
};

// ==========================================================================
// Bi-Temporal Timeline Lineage
// ==========================================================================
function renderTimeline() {
  if (!timelineList) return;
  timelineList.innerHTML = "";

  if (activeMemories.length === 0) {
    timelineList.innerHTML = `<div class="timeline-empty">No memory trajectories recorded yet.</div>`;
    return;
  }

  const sorted = [...activeMemories].sort((a, b) => new Date(b.valid_from) - new Date(a.valid_from));

  sorted.forEach(m => {
    const node = document.createElement("div");
    node.className = `timeline-node ${m.is_active ? 'active' : 'archived'}`;

    const dateStr = new Date(m.valid_from).toLocaleString([], {
      month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit"
    });
    const stateTag = m.is_active
      ? `<span style="color: var(--color-emerald); font-weight: 600;">Active Knowledge</span>`
      : `<span style="color: var(--text-muted); font-weight: 500;">Superseded / Closed Window</span>`;

    const icon = m.is_active ? "●" : "○";

    node.innerHTML = `
      <div class="timeline-icon-col" style="color: ${m.is_active ? 'var(--color-emerald)' : 'var(--text-faint)'};">${icon}</div>
      <div class="timeline-content">
        <div class="timeline-meta-row">
          <span>${dateStr}</span>
          <span>·</span>
          <span>${stateTag}</span>
          <span>·</span>
          <span class="badge-tag ${m.category.toLowerCase()}">${m.category}</span>
        </div>
        <div class="timeline-fact-title">${escapeHtml(m.fact)}</div>
        <small style="color: var(--text-muted); font-family: var(--font-mono); font-size: 10px;">
          Subject: ${escapeHtml(m.subject)} · Predicate: ${escapeHtml(m.predicate)} · Object: ${escapeHtml(m.object)}
        </small>
      </div>
    `;

    timelineList.appendChild(node);
  });
}

// ==========================================================================
// Decay Telemetry Dashboard
// ==========================================================================
function updateTelemetry() {
  const activeNodes = activeMemories.filter(m => m.is_active);
  const ymylNodes = activeNodes.filter(m => m.ymyl_protected);
  const archivedNodes = activeMemories.filter(m => !m.is_active);

  const activeEl = document.getElementById("telemetry-active-count");
  const ymylEl = document.getElementById("telemetry-ymyl-count");
  const archivedEl = document.getElementById("telemetry-archived-count");
  const stabilityEl = document.getElementById("telemetry-avg-stability");

  if (activeEl) activeEl.textContent = activeNodes.length;
  if (ymylEl) ymylEl.textContent = ymylNodes.length;
  if (archivedEl) archivedEl.textContent = archivedNodes.length;

  if (stabilityEl) {
    if (activeNodes.length === 0) {
      stabilityEl.textContent = "1.0d";
    } else {
      const avg = activeNodes.reduce((acc, n) => acc + (n.stability || 1.0), 0) / activeNodes.length;
      stabilityEl.textContent = `${avg.toFixed(1)}d`;
    }
  }
}

// ==========================================================================
// Success Compass (Morning Brief & Commitments)
// ==========================================================================
async function loadCompass() {
  try {
    const res = await fetch(`${API_BASE}/api/success/compass`);
    if (res.ok) {
      const data = await res.json();
      if (morningBriefText) {
        morningBriefText.innerHTML = formatMarkdown(data.morning_brief);
      }
      activeCommitments = data.commitments || [];
      renderCommitments();
    }
  } catch (err) {
    console.warn("Could not load success compass:", err);
  }
}

function renderCommitments() {
  if (!commitmentsList) return;
  commitmentsList.innerHTML = "";

  const pendingList = activeCommitments.filter(c => c.status !== "completed");
  if (commitmentsCounter) {
    commitmentsCounter.textContent = `${pendingList.length} active`;
  }

  if (activeCommitments.length === 0) {
    commitmentsList.innerHTML = `
      <div style="font-size: 11.5px; color: var(--text-muted); padding: 8px 0;">
        No commitments recorded. Use the input above to set today's needle-moving priorities.
      </div>
    `;
    return;
  }

  activeCommitments.forEach(c => {
    const isCompleted = c.status === "completed";
    const item = document.createElement("div");
    item.className = `commitment-item ${isCompleted ? 'completed' : ''}`;

    let deadlineBadge = "";
    if (c.deadline) {
      const due = new Date(c.deadline);
      const isOverdue = due < new Date() && !isCompleted;
      deadlineBadge = `<span class="commitment-deadline ${isOverdue ? 'overdue' : ''}">Due ${due.toLocaleDateString([], { month: "short", day: "numeric" })}</span>`;
    }

    item.innerHTML = `
      <input type="checkbox" class="commitment-checkbox" ${isCompleted ? 'checked' : ''} onchange="toggleCommitment('${c.id}', this.checked)">
      <div class="commitment-info">
        <div class="commitment-title">${escapeHtml(c.title)}</div>
        ${deadlineBadge}
      </div>
    `;

    commitmentsList.appendChild(item);
  });
}

// Inline Goal Add
if (formQuickGoal) {
  formQuickGoal.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = inputQuickGoal.value.trim();
    if (!title) return;

    try {
      const res = await fetch(`${API_BASE}/api/success/commitments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title }),
      });
      if (res.ok) {
        inputQuickGoal.value = "";
        showToast("Goal added to Commitment Loop.", "success");
        await loadCompass();
      }
    } catch (err) {
      showToast("Error adding goal: " + err.message, "error");
    }
  });
}

// Toggle Commitment Status
window.toggleCommitment = async function(id, isChecked) {
  const newStatus = isChecked ? "completed" : "pending";
  try {
    const res = await fetch(`${API_BASE}/api/success/commitments/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    if (res.ok) {
      const target = activeCommitments.find(c => c.id === id);
      if (target) target.status = newStatus;
      renderCommitments();
      showToast(isChecked ? "Commitment marked completed!" : "Commitment reopened.", "info");
    }
  } catch (err) {
    showToast("Failed to update commitment: " + err.message, "error");
  }
};

// Refresh Morning Brief
if (btnRefreshBrief) {
  btnRefreshBrief.addEventListener("click", async () => {
    btnRefreshBrief.style.transform = "rotate(180deg)";
    btnRefreshBrief.style.transition = "transform 0.4s ease";
    setTimeout(() => { btnRefreshBrief.style.transform = ""; }, 400);

    morningBriefText.innerHTML = `
      <div class="loading-state">
        <span class="spinner-circle"></span>
        <span>Regenerating morning brief with local LLM...</span>
      </div>
    `;
    await loadCompass();
    showToast("Morning readiness brief updated.", "info");
  });
}

// ==========================================================================
// REM Dream Consolidation Trigger
// ==========================================================================
if (btnTriggerDream) {
  btnTriggerDream.addEventListener("click", async () => {
    btnTriggerDream.disabled = true;
    btnDreamLabel.textContent = "Dreaming...";
    showToast("Triggering REM consolidation cycle in background...", "info");

    try {
      const res = await fetch(`${API_BASE}/api/dream/trigger`, { method: "POST" });
      const data = await res.json();
      const s = data.summary;
      showToast(
        `🌙 Consolidation Complete: ${s.facts_extracted} facts extracted, ${s.nodes_archived} archived, ${s.active_nodes_count} active.`,
        "success",
        5000
      );
      await loadMemories();
      await loadCompass();
    } catch (err) {
      showToast("REM Dream cycle failed: " + err.message, "error");
    } finally {
      btnTriggerDream.disabled = false;
      btnDreamLabel.textContent = "Consolidate";
    }
  });
}

// ==========================================================================
// Memory Node Add / Edit Modal
// ==========================================================================
if (btnAddMemory) {
  btnAddMemory.addEventListener("click", () => {
    document.getElementById("edit-node-id").value = "";
    document.getElementById("modal-title").textContent = "Create Personal Memory Node";
    formCreateMemory.reset();
    document.getElementById("input-subject").value = "user";
    modalAddMemory.style.display = "flex";
  });
}

if (btnCloseModal) btnCloseModal.addEventListener("click", () => { modalAddMemory.style.display = "none"; });
if (btnCancelMemory) btnCancelMemory.addEventListener("click", () => { modalAddMemory.style.display = "none"; });

window.openEditMemory = function(id) {
  const node = activeMemories.find(m => m.id === id);
  if (!node) return;

  document.getElementById("edit-node-id").value = node.id;
  document.getElementById("modal-title").textContent = "Edit Personal Memory Node";
  document.getElementById("input-subject").value = node.subject;
  document.getElementById("input-predicate").value = node.predicate;
  document.getElementById("input-object").value = node.object;
  document.getElementById("select-category").value = node.category.toLowerCase();
  document.getElementById("check-ymyl").checked = Boolean(node.ymyl_protected);
  modalAddMemory.style.display = "flex";
};

if (formCreateMemory) {
  formCreateMemory.addEventListener("submit", async (e) => {
    e.preventDefault();
    const editId = document.getElementById("edit-node-id").value.trim();

    const payload = {
      subject: document.getElementById("input-subject").value.trim(),
      predicate: document.getElementById("input-predicate").value.trim(),
      object: document.getElementById("input-object").value.trim(),
      category: document.getElementById("select-category").value,
      confidence: 1.0,
      ymyl_protected: document.getElementById("check-ymyl").checked,
    };

    try {
      const url = editId ? `${API_BASE}/api/memories/${editId}` : `${API_BASE}/api/memories`;
      const method = editId ? "PUT" : "POST";
      const res = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        modalAddMemory.style.display = "none";
        formCreateMemory.reset();
        await loadMemories();
        showToast(editId ? "Memory node updated." : "New fact committed to vault.", "success");
      } else {
        const errData = await res.json().catch(() => ({}));
        showToast("Save failed: " + (errData.detail || res.statusText), "error");
      }
    } catch (err) {
      showToast("Save failed: " + err.message, "error");
    }
  });
}

// ==========================================================================
// Nightly Reflection Modal
// ==========================================================================
if (btnOpenReflection) {
  btnOpenReflection.addEventListener("click", () => {
    formReflection.reset();
    reflectionResponseBox.style.display = "none";
    modalReflection.style.display = "flex";
  });
}

if (btnCloseReflection) btnCloseReflection.addEventListener("click", () => { modalReflection.style.display = "none"; });
if (btnCancelReflection) btnCancelReflection.addEventListener("click", () => { modalReflection.style.display = "none"; });

if (formReflection) {
  formReflection.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = reflectionInput.value.trim();
    if (!text) return;

    reflectionResponseBox.style.display = "block";
    reflectionResponseText.innerHTML = `
      <div class="loading-state">
        <span class="spinner-circle"></span>
        <span>Processing reflection and winding down runway...</span>
      </div>
    `;

    try {
      const res = await fetch(`${API_BASE}/api/success/reflection`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brain_dump: text }),
      });
      if (res.ok) {
        const data = await res.json();
        reflectionResponseText.innerHTML = formatMarkdown(data.response);
        showToast("Evening reflection recorded.", "success");
      }
    } catch (err) {
      reflectionResponseText.textContent = "Error: " + err.message;
    }
  });
}

// ==========================================================================
// Global Keyboard Shortcuts
// ==========================================================================
window.addEventListener("keydown", (e) => {
  const isMeta = e.metaKey || e.ctrlKey;

  // ⌘D -> Trigger Dream
  if (isMeta && e.key.toLowerCase() === "d") {
    e.preventDefault();
    if (btnTriggerDream) btnTriggerDream.click();
  }

  // ⌘N -> Add Memory
  if (isMeta && e.key.toLowerCase() === "n") {
    e.preventDefault();
    if (btnAddMemory) btnAddMemory.click();
  }

  // ⌘K -> Switch to Mindstream & Focus Search
  if (isMeta && e.key.toLowerCase() === "k") {
    e.preventDefault();
    const tab = document.getElementById("tab-btn-mindstream");
    if (tab) tab.click();
    if (vaultSearchInput) {
      setTimeout(() => vaultSearchInput.focus(), 50);
    }
  }

  // Escape -> Close Modals
  if (e.key === "Escape") {
    if (modalAddMemory) modalAddMemory.style.display = "none";
    if (modalReflection) modalReflection.style.display = "none";
  }
});

// ==========================================================================
// Formatting Helpers
// ==========================================================================
function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

function formatMarkdown(text) {
  if (!text) return "";
  let s = escapeHtml(text);

  // Bold **text**
  s = s.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Italic *text*
  s = s.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // Inline code `code`
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Markdown links [text](url)
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  // Bullet lines
  s = s.replace(/^[-*•]\s+(.*)$/gm, '• $1');
  // Linebreaks
  s = s.replace(/\n\n+/g, '</p><p>').replace(/\n/g, '<br>');

  return s;
}

// Initial Data Loading
loadMemories();
loadCompass();
