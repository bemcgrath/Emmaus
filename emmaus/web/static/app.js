const state = {
  userId: localStorage.getItem("emmaus.userId") || "demo-user",
  activeScreen: "home",
  selectedMood: "neutral",
  activeSession: null,
  currentQuestion: null,
  recommendation: null,
  nudge: null,
  profile: null,
  textSources: [],
};

const elements = {};

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  bindEvents();
  initializeDefaults();
  loadApp().catch(handleError);
});

function cacheElements() {
  Object.assign(elements, {
    screens: Array.from(document.querySelectorAll(".screen")),
    navButtons: Array.from(document.querySelectorAll("[data-nav-target]")),
    toast: document.getElementById("toast"),
    refreshButton: document.getElementById("refresh-button"),
    previewNudgeButton: document.getElementById("preview-nudge-button"),
    identityForm: document.getElementById("identity-form"),
    userIdInput: document.getElementById("user-id-input"),
    displayNameInput: document.getElementById("display-name-input"),
    preferredMinutesInput: document.getElementById("preferred-minutes-input"),
    guideModeSelect: document.getElementById("guide-mode-select"),
    streakValue: document.getElementById("streak-value"),
    streakCopy: document.getElementById("streak-copy"),
    openActionCount: document.getElementById("open-action-count"),
    openActionCopy: document.getElementById("open-action-copy"),
    recommendationCard: document.getElementById("recommendation-card"),
    focusPill: document.getElementById("focus-pill"),
    moodForm: document.getElementById("mood-form"),
    moodChipRow: document.getElementById("mood-chip-row"),
    energySelect: document.getElementById("energy-select"),
    moodNotes: document.getElementById("mood-notes"),
    latestMoodCopy: document.getElementById("latest-mood-copy"),
    sessionForm: document.getElementById("session-form"),
    entryPointInput: document.getElementById("entry-point-input"),
    requestedMinutesInput: document.getElementById("requested-minutes-input"),
    sessionGuideMode: document.getElementById("session-guide-mode"),
    textSourceSelect: document.getElementById("text-source-select"),
    sessionStatusPill: document.getElementById("session-status-pill"),
    sessionReference: document.getElementById("session-reference"),
    questionProgressPill: document.getElementById("question-progress-pill"),
    sessionHero: document.getElementById("session-hero"),
    passageText: document.getElementById("passage-text"),
    sessionPlan: document.getElementById("session-plan"),
    commentaryBlock: document.getElementById("commentary-block"),
    currentQuestionHeading: document.getElementById("current-question-heading"),
    currentQuestionCopy: document.getElementById("current-question-copy"),
    responseForm: document.getElementById("response-form"),
    responseText: document.getElementById("response-text"),
    engagementInput: document.getElementById("engagement-input"),
    submitResponseButton: document.getElementById("submit-response-button"),
    completeForm: document.getElementById("complete-form"),
    summaryNotes: document.getElementById("summary-notes"),
    actionItemTitle: document.getElementById("action-item-title"),
    actionItemDetail: document.getElementById("action-item-detail"),
    completeSessionButton: document.getElementById("complete-session-button"),
    actionSummaryPill: document.getElementById("action-summary-pill"),
    actionItemList: document.getElementById("action-item-list"),
    nudgeTimingPill: document.getElementById("nudge-timing-pill"),
    nudgeCard: document.getElementById("nudge-card"),
    nudgePreviewForm: document.getElementById("nudge-preview-form"),
    previewAtInput: document.getElementById("preview-at-input"),
    heroTitle: document.getElementById("hero-title"),
    heroCopy: document.getElementById("hero-copy"),
  });
}

function bindEvents() {
  elements.navButtons.forEach((button) => {
    button.addEventListener("click", () => showScreen(button.dataset.navTarget));
  });

  elements.refreshButton.addEventListener("click", () => loadDashboard().catch(handleError));
  elements.previewNudgeButton.addEventListener("click", () => {
    showScreen("nudges");
    loadNudgePreview().catch(handleError);
  });

  elements.identityForm.addEventListener("submit", onSaveIdentity);
  elements.moodForm.addEventListener("submit", onSaveMood);
  elements.sessionForm.addEventListener("submit", onStartSession);
  elements.responseForm.addEventListener("submit", onSubmitResponse);
  elements.completeForm.addEventListener("submit", onCompleteSession);
  elements.nudgePreviewForm.addEventListener("submit", onPreviewNudgeAtTime);

  elements.moodChipRow.querySelectorAll(".choice-chip").forEach((chip) => {
    chip.addEventListener("click", () => selectMood(chip.dataset.value));
  });

  elements.actionItemList.addEventListener("click", onActionListClick);
}

function initializeDefaults() {
  elements.userIdInput.value = state.userId;
  selectMood(state.selectedMood);
}

async function loadApp() {
  await loadTextSources();
  await loadDashboard();
}

async function loadDashboard() {
  const userId = getUserId();
  localStorage.setItem("emmaus.userId", userId);

  const [profile, recommendation, streaks, openItems, latestMood] = await Promise.all([
    fetchJson(`/v1/users/${encodeURIComponent(userId)}/profile`),
    fetchJson(`/v1/agent/recommendations/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/engagement/streaks/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/action-items/${encodeURIComponent(userId)}?status=open`),
    fetchJson(`/v1/study/mood/${encodeURIComponent(userId)}`, { allowNull: true }),
  ]);

  state.profile = profile;
  state.recommendation = recommendation;

  renderProfile(profile);
  renderRecommendation(recommendation);
  renderStreaks(streaks);
  renderActionItems(openItems.items || []);
  renderLatestMood(latestMood);
  await loadNudgePreview();
}

async function loadTextSources() {
  const response = await fetchJson("/v1/sources/text");
  state.textSources = response.sources || response;
  const options = state.textSources
    .map((source) => `<option value="${escapeHtml(source.source_id)}">${escapeHtml(source.name)}</option>`)
    .join("");
  elements.textSourceSelect.innerHTML = options || '<option value="sample_local">Sample Public Domain Local Source</option>';
}
function renderProfile(profile) {
  const name = profile.display_name || "friend";
  elements.heroTitle.textContent = `Walk with Christ through Scripture, ${name}.`;
  elements.heroCopy.textContent = "Emmaus guides short, honest sessions that test understanding, surface gaps, and end with a real next step.";
  elements.displayNameInput.value = profile.display_name || "";
  elements.preferredMinutesInput.value = profile.preferences.preferred_session_minutes || 20;
  elements.guideModeSelect.value = profile.preferences.preferred_guide_mode || "guide";

  const preferredSource = profile.preferences.preferred_translation_source_id;
  if (preferredSource && Array.from(elements.textSourceSelect.options).some((option) => option.value === preferredSource)) {
    elements.textSourceSelect.value = preferredSource;
  }
}

function renderRecommendation(recommendation) {
  elements.focusPill.textContent = capitalize(recommendation.focus_area);
  elements.recommendationCard.innerHTML = `
    <article class="recommendation-card">
      <div class="recommendation-meta">
        <span class="meta-pill">${escapeHtml(formatReference(recommendation.recommended_reference))}</span>
        <span class="meta-pill">${escapeHtml(recommendation.recommended_guide_mode)}</span>
        <span class="meta-pill">${escapeHtml(`${recommendation.recommended_minutes} min`)}</span>
      </div>
      <h3>${escapeHtml(recommendation.reason)}</h3>
      <p>${escapeHtml(recommendation.suggested_action)}</p>
      <p class="micro-copy">Entry point: ${escapeHtml(recommendation.recommended_entry_point)}</p>
    </article>
  `;

  elements.entryPointInput.value = recommendation.recommended_entry_point;
  elements.requestedMinutesInput.value = recommendation.recommended_minutes;
  elements.sessionGuideMode.value = "";
}

function renderStreaks(streaks) {
  const streak = streaks.current_streak || 0;
  elements.streakValue.textContent = `${streak} day streak`;
  elements.streakCopy.textContent = streak > 0
    ? `You have completed ${streaks.completed_sessions} sessions and your longest streak is ${streaks.longest_streak}.`
    : "Complete a session today to establish a rhythm.";
}

function renderActionItems(items) {
  const openCount = items.length;
  elements.openActionCount.textContent = String(openCount);
  elements.openActionCopy.textContent = openCount > 0
    ? items[0].title
    : "Your next step will show up here.";
  elements.actionSummaryPill.textContent = `${openCount} open`;

  if (!items.length) {
    elements.actionItemList.innerHTML = '<p class="empty-state">No open action items yet. Finish a session and Emmaus will turn it into a practical step.</p>';
    return;
  }

  elements.actionItemList.innerHTML = items.map((item) => `
    <article class="action-card ${item.status === "completed" ? "completed" : ""}">
      <div class="action-card-header">
        <div>
          <p class="panel-label">${escapeHtml(item.status)}</p>
          <h3>${escapeHtml(item.title)}</h3>
        </div>
        ${item.status === "open" ? `<button class="action-button" type="button" data-action="complete-item" data-id="${escapeHtml(item.action_item_id)}">Mark done</button>` : ""}
      </div>
      <p>${escapeHtml(item.detail)}</p>
      <p class="micro-copy">Created ${formatDate(item.created_at)}</p>
    </article>
  `).join("");
}

function renderLatestMood(mood) {
  if (!mood) {
    elements.latestMoodCopy.textContent = "No mood check-in saved yet.";
    return;
  }

  state.selectedMood = mood.mood;
  selectMood(mood.mood);
  elements.energySelect.value = mood.energy;
  elements.moodNotes.value = mood.notes || "";
  elements.latestMoodCopy.textContent = `Latest check-in: ${capitalize(mood.mood)} with ${mood.energy} energy.`;
}

async function loadNudgePreview(previewAt = null) {
  const payload = { user_id: getUserId() };
  if (previewAt) {
    payload.preview_at = previewAt;
  }

  const nudge = await fetchJson("/v1/agent/nudges/preview", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  state.nudge = nudge;
  renderNudge(nudge);
}

function renderNudge(nudge) {
  elements.nudgeTimingPill.textContent = formatTimingDecision(nudge.timing_decision);
  elements.nudgeCard.innerHTML = `
    <article class="nudge-card">
      <div class="nudge-meta">
        <span class="meta-pill">${escapeHtml(nudge.nudge_type)}</span>
        <span class="meta-pill">${escapeHtml(nudge.recommended_guide_mode)}</span>
        <span class="meta-pill">${escapeHtml(`${nudge.recommended_minutes} min`)}</span>
      </div>
      <h3>${escapeHtml(nudge.title)}</h3>
      <p>${escapeHtml(nudge.message)}</p>
      <p><strong>Why now:</strong> ${escapeHtml(nudge.timing_reason)}</p>
      <p><strong>Suggested entry:</strong> ${escapeHtml(nudge.recommended_entry_point)}</p>
      <p class="micro-copy">Timezone: ${escapeHtml(nudge.local_timezone)}${nudge.scheduled_for ? ` | Scheduled for ${escapeHtml(formatDateTime(nudge.scheduled_for))}` : ""}</p>
    </article>
  `;
}

function renderSessionStart(payload) {
  state.activeSession = payload.session;
  state.currentQuestion = payload.current_question;
  elements.sessionStatusPill.textContent = capitalize(payload.session.status);
  elements.sessionReference.textContent = formatReference(payload.session.reference);
  elements.sessionHero.innerHTML = `
    <article class="inline-card">
      <div class="session-meta">
        <span class="meta-pill">${escapeHtml(payload.session.guide_mode)}</span>
        <span class="meta-pill">${escapeHtml(`${payload.session.requested_minutes} min`)}</span>
        <span class="meta-pill">${escapeHtml(payload.recommendation.focus_area)}</span>
      </div>
      <p>${escapeHtml(payload.session.latest_message)}</p>
    </article>
  `;
  elements.passageText.textContent = payload.passage.text;
  elements.sessionPlan.innerHTML = payload.session.plan
    .map((step) => `
      <article class="inline-card">
        <p class="panel-label">${escapeHtml(`${step.estimated_minutes} min`)}</p>
        <h3>${escapeHtml(step.title)}</h3>
        <p>${escapeHtml(step.instruction)}</p>
      </article>
    `)
    .join("");

  const notes = payload.commentary || [];
  elements.commentaryBlock.innerHTML = notes.length
    ? notes.map((note) => `
      <article class="commentary-note">
        <p class="panel-label">Commentary</p>
        <h3>${escapeHtml(note.title)}</h3>
        <p>${escapeHtml(note.body)}</p>
      </article>
    `).join("")
    : '<p class="empty-state">No commentary note is attached to this session yet.</p>';

  renderCurrentQuestion(payload.current_question, payload.session.questions.length, payload.session.current_question_index);
  showScreen("session");
}

function renderCurrentQuestion(question, totalQuestions, currentIndex) {
  state.currentQuestion = question;
  elements.questionProgressPill.textContent = `${Math.min(currentIndex + (question ? 1 : 0), totalQuestions)} / ${totalQuestions}`;
  if (!question) {
    elements.currentQuestionHeading.textContent = "Ready to complete";
    elements.currentQuestionCopy.textContent = "You’ve answered the core questions. Complete the session to receive your action step.";
    elements.submitResponseButton.disabled = true;
    elements.responseText.disabled = true;
    return;
  }

  elements.currentQuestionHeading.textContent = `${capitalize(question.type)} question`;
  elements.currentQuestionCopy.textContent = question.question;
  elements.submitResponseButton.disabled = false;
  elements.responseText.disabled = false;
  elements.responseText.value = "";
}

function renderSessionTurn(payload) {
  state.activeSession = payload.session;
  elements.sessionStatusPill.textContent = capitalize(payload.session.status);
  elements.sessionHero.innerHTML = `
    <article class="inline-card">
      <p>${escapeHtml(payload.reply_message)}</p>
      <p class="micro-copy">${payload.remaining_questions} questions remaining.</p>
    </article>
  `;
  renderCurrentQuestion(payload.next_question, payload.session.questions.length, payload.session.current_question_index);
}

function renderSessionComplete(payload) {
  state.activeSession = payload.session;
  elements.sessionStatusPill.textContent = "Completed";
  elements.sessionHero.innerHTML = `
    <article class="inline-card">
      <p>${escapeHtml(payload.session.latest_message)}</p>
      <div class="session-meta">
        <span class="meta-pill">Streak ${escapeHtml(String(payload.engagement.current_streak))}</span>
        <span class="meta-pill">${escapeHtml(String(payload.engagement.completed_sessions))} completed</span>
      </div>
    </article>
  `;
  elements.currentQuestionHeading.textContent = "Action item ready";
  elements.currentQuestionCopy.textContent = payload.action_item.title;
  elements.responseText.value = "";
  elements.responseText.disabled = true;
  elements.submitResponseButton.disabled = true;
  showToast("Session completed. Your action step is ready.");
  loadDashboard().catch(handleError);
  showScreen("actions");
}
async function onSaveIdentity(event) {
  event.preventDefault();
  const userId = getUserId();
  const payload = {
    display_name: elements.displayNameInput.value.trim() || null,
    preferred_session_minutes: numberOrNull(elements.preferredMinutesInput.value),
    preferred_guide_mode: elements.guideModeSelect.value || null,
  };

  const profile = await fetchJson(`/v1/users/${encodeURIComponent(userId)}/preferences`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  state.profile = profile;
  renderProfile(profile);
  showToast("Guide preferences saved.");
  await loadDashboard();
}

async function onSaveMood(event) {
  event.preventDefault();
  await fetchJson("/v1/study/mood", {
    method: "POST",
    body: JSON.stringify({
      user_id: getUserId(),
      mood: state.selectedMood,
      energy: elements.energySelect.value,
      notes: elements.moodNotes.value.trim() || null,
    }),
  });
  showToast("Mood check-in saved.");
  await loadDashboard();
}

async function onStartSession(event) {
  event.preventDefault();
  const payload = {
    user_id: getUserId(),
    display_name: elements.displayNameInput.value.trim() || null,
    text_source_id: elements.textSourceSelect.value || null,
    entry_point: elements.entryPointInput.value.trim() || "continue where I left off",
    requested_minutes: numberOrNull(elements.requestedMinutesInput.value),
    guide_mode: elements.sessionGuideMode.value || null,
  };

  const session = await fetchJson("/v1/agent/session/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderSessionStart(session);
  showToast("Session started.");
}

async function onSubmitResponse(event) {
  event.preventDefault();
  if (!state.activeSession || !state.currentQuestion) {
    showToast("Start a session first.");
    return;
  }

  const text = elements.responseText.value.trim();
  if (!text) {
    showToast("Write a response before sending it.");
    return;
  }

  const payload = {
    session_id: state.activeSession.session_id,
    user_id: getUserId(),
    response_text: text,
    engagement_score: Number(elements.engagementInput.value || 4),
  };

  const turn = await fetchJson("/v1/agent/session/respond", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderSessionTurn(turn);
}

async function onCompleteSession(event) {
  event.preventDefault();
  if (!state.activeSession) {
    showToast("Start a session first.");
    return;
  }

  const payload = {
    session_id: state.activeSession.session_id,
    user_id: getUserId(),
    summary_notes: elements.summaryNotes.value.trim() || null,
    action_item_title: elements.actionItemTitle.value.trim() || null,
    action_item_detail: elements.actionItemDetail.value.trim() || null,
    engagement_score: Number(elements.engagementInput.value || 4),
  };

  const completed = await fetchJson("/v1/agent/session/complete", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderSessionComplete(completed);
}

async function onActionListClick(event) {
  const button = event.target.closest("[data-action='complete-item']");
  if (!button) {
    return;
  }

  await fetchJson(`/v1/study/action-items/${encodeURIComponent(button.dataset.id)}/complete`, {
    method: "POST",
    body: JSON.stringify({ user_id: getUserId() }),
  });
  showToast("Action item completed.");
  await loadDashboard();
}

async function onPreviewNudgeAtTime(event) {
  event.preventDefault();
  const previewValue = elements.previewAtInput.value;
  const previewAt = previewValue ? new Date(previewValue).toISOString() : null;
  await loadNudgePreview(previewAt);
  showToast("Nudge preview refreshed.");
}

function showScreen(screenName) {
  state.activeScreen = screenName;
  elements.screens.forEach((screen) => {
    screen.classList.toggle("screen-active", screen.dataset.screen === screenName);
  });
  document.querySelectorAll(".nav-pill").forEach((button) => {
    button.classList.toggle("nav-pill-active", button.dataset.navTarget === screenName);
  });
}

function selectMood(mood) {
  state.selectedMood = mood;
  elements.moodChipRow.querySelectorAll(".choice-chip").forEach((chip) => {
    chip.classList.toggle("choice-chip-active", chip.dataset.value === mood);
  });
}

async function fetchJson(url, options = {}) {
  const fetchOptions = {
    headers: { "Content-Type": "application/json" },
    ...options,
  };

  const response = await fetch(url, fetchOptions);
  if (response.status === 404 && options.allowNull) {
    return null;
  }
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("toast-visible");
  window.clearTimeout(showToast.timeoutId);
  showToast.timeoutId = window.setTimeout(() => {
    elements.toast.classList.remove("toast-visible");
  }, 2200);
}

function handleError(error) {
  console.error(error);
  showToast(typeof error?.message === "string" ? error.message : "Something went wrong.");
}
function getUserId() {
  return elements.userIdInput.value.trim() || "demo-user";
}

function numberOrNull(value) {
  if (value === "" || value == null) {
    return null;
  }
  return Number(value);
}

function capitalize(value) {
  if (!value) {
    return "";
  }
  return value.charAt(0).toUpperCase() + value.slice(1).replaceAll("_", " ");
}

function formatReference(reference) {
  if (!reference) {
    return "Recommended reading";
  }
  const range = reference.end_verse ? `${reference.start_verse}-${reference.end_verse}` : `${reference.start_verse}`;
  return `${reference.book} ${reference.chapter}:${range}`;
}

function formatTimingDecision(decision) {
  if (decision === "later_today") {
    return "Later today";
  }
  if (decision === "not_today") {
    return "Not today";
  }
  return "Send now";
}

function formatDate(value) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(new Date(value));
}

function formatDateTime(value) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
