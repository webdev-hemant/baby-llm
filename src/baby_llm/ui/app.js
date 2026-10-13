/**
 * Baby LLM: Glass-Box Frontend Engine
 */

const API_BASE = window.location.origin.startsWith("http")
  ? window.location.origin
  : "http://127.0.0.1:21225";

// State
let activeMemories = [];
let activeCategory = "all";

// DOM Elements
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const memoryCardsContainer = document.getElementById("memory-cards-container");
const memoryCount = document.getElementById("memory-count");
const morningBriefText = document.getElementById("morning-brief-text");
const commitmentsList = document.getElementById("commitments-list");
const timelineList = document.getElementById("timeline-list");
const btnTriggerDream = document.getElementById("btn-trigger-dream");
const modalAddMemory = document.getElementById("modal-add-memory");
const btnAddMemory = document.getElementById("btn-add-memory");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelMemory = document.getElementById("btn-cancel-memory");
const formCreateMemory = document.getElementById("form-create-memory");
const activeVramText = document.getElementById("active-vram-text");
const toggleIncognito = document.getElementById("toggle-incognito");
const incognitoPillText = document.getElementById("incognito-pill-text");

if (toggleIncognito) {
  toggleIncognito.addEventListener("change", () => {
    if (toggleIncognito.checked) {
      if (incognitoPillText) incognitoPillText.textContent = "🕵️ Incognito: ON";
      if (chatInput) chatInput.placeholder = "🕵️ Incognito: Private prompt (WAL logging bypassed)...";
    } else {
      if (incognitoPillText) incognitoPillText.textContent = "🕵️ Incognito: Off";
      if (chatInput) chatInput.placeholder = "Type a thought, goal, or life update...";
    }
  });
}

// Tab Switching
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    btn.classList.add("active");

    if (btn.id === "tab-btn-chat") {
      document.getElementById("view-chat").classList.add("active");
    } else if (btn.id === "tab-btn-mindstream") {
      document.getElementById("view-mindstream").classList.add("active");
      loadMemories();
    } else if (btn.id === "tab-btn-timeline") {
      document.getElementById("view-timeline").classList.add("active");
      renderTimeline();
    }
  });
});

// Category Filter Pills
document.querySelectorAll(".filter-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    activeCategory = pill.dataset.category;
    renderMemoryCards();
  });
});

// Chat Submission
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  // Append user bubble
  appendMessage(text, "user");
  chatInput.value = "";

  // Show typing placeholder
  const placeholderId = appendMessage("Thinking locally...", "assistant", true);

  // Check incognito state
  const isIncognito = toggleIncognito && toggleIncognito.checked;

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, incognito: isIncognito }),
    });
    const data = await res.json();
    updateMessage(placeholderId, data.reply);
  } catch (err) {
    updateMessage(
      placeholderId,
      `⚠️ Offline note: Saved to local storage. (Could not connect to FastAPI server at ${API_BASE})`
    );
  }
});

function appendMessage(text, sender, isPlaceholder = false) {
  const id = "msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 4);
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}-msg`;
  msgDiv.id = id;

  const avatar = sender === "user" ? "👤" : "👶";
  msgDiv.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-bubble">
      <p>${escapeHtml(text)}</p>
    </div>
  `;
  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function updateMessage(id, newText) {
  const msgDiv = document.getElementById(id);
  if (msgDiv) {
    const bubble = msgDiv.querySelector(".msg-bubble");
    if (bubble) {
      bubble.innerHTML = `<p>${formatMarkdown(newText)}</p>`;
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

// Mindstream Memory Operations
async function loadMemories() {
  try {
    const res = await fetch(`${API_BASE}/api/memories?active_only=false`);
    if (res.ok) {
      activeMemories = await res.json();
      memoryCount.textContent = activeMemories.filter(m => m.is_active).length;
      renderMemoryCards();
    }
  } catch (err) {
    console.warn("Could not fetch memories from API:", err);
  }
}

function renderMemoryCards() {
  memoryCardsContainer.innerHTML = "";
  const filtered = activeMemories.filter(m => {
    if (!m.is_active) return false;
    if (activeCategory === "all") return true;
    return m.category.toLowerCase() === activeCategory.toLowerCase();
  });

  if (filtered.length === 0) {
    memoryCardsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); text-align: center; padding: 40px 0;">No memories found in this category. Talk to Baby LLM or click "+ Add Memory"!</div>`;
    return;
  }

  filtered.forEach(m => {
    const card = document.createElement("div");
    card.className = "memory-card";
    const ymylShield = m.ymyl_protected ? `<span class="ymyl-badge" title="Immune to temporal decay">🛡️ YMYL</span>` : "";
    card.innerHTML = `
      <div class="card-top">
        <span class="category-tag ${m.category.toLowerCase()}">${m.category}</span>
        ${ymylShield}
      </div>
      <div class="fact-text">${escapeHtml(m.fact)}</div>
      <div class="card-meta">
        <span>Conf: ${Math.round(m.confidence * 100)}% • Stab: ${m.stability.toFixed(1)}</span>
        <div class="card-actions-group">
          <button class="btn-card-action btn-card-edit" onclick="openEditMemory('${m.id}')" title="Edit memory node">Edit</button>
          <button class="btn-card-action" onclick="eraseMemory('${m.id}')" title="Permanently erase memory node">Erase</button>
        </div>
      </div>
    `;
    memoryCardsContainer.appendChild(card);
  });
}

// Bi-temporal Timeline View
function renderTimeline() {
  timelineList.innerHTML = "";
  if (activeMemories.length === 0) {
    timelineList.innerHTML = `<div class="timeline-empty">No memory trajectories recorded yet.</div>`;
    return;
  }

  // Sort by valid_from descending
  const sorted = [...activeMemories].sort((a, b) => new Date(b.valid_from) - new Date(a.valid_from));
  sorted.forEach(m => {
    const item = document.createElement("div");
    item.className = `timeline-item ${m.is_active ? 'active' : 'archived'}`;
    const dateStr = new Date(m.valid_from).toLocaleDateString(undefined, {
      month: "short", day: "numeric", year: "numeric"
    });
    const statusLabel = m.is_active ? '<span style="color: #34D399;">(Active Fact)</span>' : '<span style="color: #94A3B8;">(Archived/Overwritten)</span>';
    item.innerHTML = `
      <div class="timeline-date">${dateStr} • ${statusLabel}</div>
      <div class="timeline-fact"><strong>${escapeHtml(m.fact)}</strong></div>
      <small style="color: var(--text-muted); font-size: 0.72rem;">Category: ${m.category} • Subject: ${m.subject}</small>
    `;
    timelineList.appendChild(item);
  });
}

// One-click Erase Memory Node
window.eraseMemory = async function(id) {
  if (!confirm("Are you sure you want to permanently erase this personal memory node?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/memories/${id}`, { method: "DELETE" });
    if (res.ok) {
      activeMemories = activeMemories.filter(m => m.id !== id);
      renderMemoryCards();
      renderTimeline();
      memoryCount.textContent = activeMemories.filter(m => m.is_active).length;
    }
  } catch (err) {
    alert("Failed to erase node: " + err.message);
  }
};

// Success Compass
async function loadCompass() {
  try {
    const res = await fetch(`${API_BASE}/api/success/compass`);
    if (res.ok) {
      const data = await res.json();
      morningBriefText.textContent = data.morning_brief;
      renderCommitments(data.commitments);
    }
  } catch (err) {
    console.warn("Could not load success compass:", err);
  }
}

function renderCommitments(list) {
  commitmentsList.innerHTML = "";
  if (!list || list.length === 0) {
    commitmentsList.innerHTML = `<div style="font-size: 0.78rem; color: var(--text-muted);">No active commitments. Tell Baby LLM what you plan to accomplish today!</div>`;
    return;
  }
  list.forEach(c => {
    const div = document.createElement("div");
    div.className = "commitment-item";
    div.innerHTML = `
      <input type="checkbox" id="commit-${c.id}">
      <label for="commit-${c.id}" style="cursor: pointer; flex: 1;">${escapeHtml(c.title)}</label>
    `;
    commitmentsList.appendChild(div);
  });
}

// REM Dream Consolidation Trigger
btnTriggerDream.addEventListener("click", async () => {
  activeVramText.textContent = "Dreaming...";
  btnTriggerDream.disabled = true;
  btnTriggerDream.innerHTML = "<span>🌙 Consolidating...</span>";

  try {
    const res = await fetch(`${API_BASE}/api/dream/trigger`, { method: "POST" });
    const data = await res.json();
    alert(`🌙 REM Dream Cycle Complete!\nTurns Processed: ${data.summary.turns_processed}\nFacts Extracted: ${data.summary.facts_extracted}\nActive Nodes: ${data.summary.active_nodes_count}`);
    await loadMemories();
    await loadCompass();
  } catch (err) {
    alert("Dream consolidation trigger failed: " + err.message);
  } finally {
    activeVramText.textContent = "SLM: Idle";
    btnTriggerDream.disabled = false;
    btnTriggerDream.innerHTML = "<span>🌙 Trigger Dream</span>";
  }
});

// Add / Edit Memory Modal Handlers
btnAddMemory.addEventListener("click", () => {
  const editIdEl = document.getElementById("edit-node-id");
  if (editIdEl) editIdEl.value = "";
  const titleEl = document.getElementById("modal-title");
  if (titleEl) titleEl.textContent = "Create Personal Memory Node";
  formCreateMemory.reset();
  document.getElementById("input-subject").value = "user";
  modalAddMemory.style.display = "flex";
});

btnCloseModal.addEventListener("click", () => { modalAddMemory.style.display = "none"; });
btnCancelMemory.addEventListener("click", () => { modalAddMemory.style.display = "none"; });

window.openEditMemory = function(id) {
  const node = activeMemories.find(m => m.id === id);
  if (!node) return;
  const editIdEl = document.getElementById("edit-node-id");
  if (editIdEl) editIdEl.value = node.id;
  const titleEl = document.getElementById("modal-title");
  if (titleEl) titleEl.textContent = "Edit Personal Memory Node";

  document.getElementById("input-subject").value = node.subject;
  document.getElementById("input-predicate").value = node.predicate;
  document.getElementById("input-object").value = node.object;
  document.getElementById("select-category").value = node.category.toLowerCase();
  document.getElementById("check-ymyl").checked = Boolean(node.ymyl_protected);
  modalAddMemory.style.display = "flex";
};

formCreateMemory.addEventListener("submit", async (e) => {
  e.preventDefault();
  const editIdEl = document.getElementById("edit-node-id");
  const editId = editIdEl ? editIdEl.value.trim() : "";

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
      if (editIdEl) editIdEl.value = "";
      await loadMemories();
    } else {
      const errData = await res.json().catch(() => ({}));
      alert("Error saving memory: " + (errData.detail || res.statusText));
    }
  } catch (err) {
    alert("Error saving memory: " + err.message);
  }
});

// Utilities
function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

function formatMarkdown(text) {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

// Initial Data Fetch
loadMemories();
loadCompass();
