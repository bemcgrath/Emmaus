const state = {
  userId: localStorage.getItem("emmaus.userId") || "demo-user",
  activeScreen: localStorage.getItem("emmaus.activeScreen") || "home",
  selectedMood: "neutral",
  selectedStudyDays: [],
  selectedActionItemId: null,
  activeSessionPayload: null,
  currentQuestion: null,
  recommendation: null,
  nudge: null,
  nudgePlan: null,
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
    heroPrimaryButton: document.getElementById("hero-primary-button"),
    previewNudgeButton: document.getElementById("preview-nudge-button"),
    onboardingPanel: document.getElementById("onboarding-panel"),
    onboardingCopy: document.getElementById("onboarding-copy"),
    todayPlanPill: document.getElementById("today-plan-pill"),
    todayPlanCard: document.getElementById("today-plan-card"),
    identityForm: document.getElementById("identity-form"),
    userIdInput: document.getElementById("user-id-input"),
    displayNameInput: document.getElementById("display-name-input"),
    preferredMinutesInput: document.getElementById("preferred-minutes-input"),
    guideModeSelect: document.getElementById("guide-mode-select"),
    preferredSourceSelect: document.getElementById("preferred-source-select"),
    nudgeIntensitySelect: document.getElementById("nudge-intensity-select"),
    timezoneInput: document.getElementById("timezone-input"),
    studyDaysRow: document.getElementById("study-days-row"),
    studyWindowStartInput: document.getElementById("study-window-start-input"),
    studyWindowEndInput: document.getElementById("study-window-end-input"),
    quietHoursStartInput: document.getElementById("quiet-hours-start-input"),
    quietHoursEndInput: document.getElementById("quiet-hours-end-input"),
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
    sessionFormCopy: document.getElementById("session-form-copy"),
    sessionFormButton: document.getElementById("session-form-button"),
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
    actionSummaryPill: document.getElementById("action-summary-pill"),
    actionItemList: document.getElementById("action-item-list"),
    actionFollowUpForm: document.getElementById("action-follow-up-form"),
    followUpTargetCopy: document.getElementById("follow-up-target-copy"),
    followUpOutcomeSelect: document.getElementById("follow-up-outcome-select"),
    followUpNoteInput: document.getElementById("follow-up-note-input"),
    followUpSubmitButton: document.getElementById("follow-up-submit-button"),
    nudgeTimingPill: document.getElementById("nudge-timing-pill"),
    nudgeCard: document.getElementById("nudge-card"),
    nudgePlanCard: document.getElementById("nudge-plan-card"),
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

  elements.refreshButton.addEventListener("click", () => loadDashboard({ restoreScreen: false }).catch(handleError));
  elements.heroPrimaryButton.addEventListener("click", onHeroPrimaryAction);
  elements.previewNudgeButton.addEventListener("click", () => {
    showScreen("nudges");
    loadNudgeArtifacts().catch(handleError);
  });

  elements.identityForm.addEventListener("submit", onSaveIdentity);
  elements.moodForm.addEventListener("submit", onSaveMood);
  elements.sessionForm.addEventListener("submit", onStartSession);
  elements.responseForm.addEventListener("submit", onSubmitResponse);
  elements.completeForm.addEventListener("submit", onCompleteSession);
  elements.actionFollowUpForm.addEventListener("submit", onSubmitActionFollowUp);
  elements.nudgePreviewForm.addEventListener("submit", onPreviewNudgeAtTime);
  elements.todayPlanCard.addEventListener("click", onTodayPlanAction);
  elements.onboardingPanel.addEventListener("click", onOnboardingAction);
  elements.actionItemList.addEventListener("click", onActionListClick);

  elements.moodChipRow.querySelectorAll(".choice-chip").forEach((chip) => {
    chip.addEventListener("click", () => selectMood(chip.dataset.value));
  });
  elements.studyDaysRow.querySelectorAll(".choice-chip").forEach((chip) => {
    chip.addEventListener("click", () => toggleStudyDay(chip.dataset.day));
  });
}

function initializeDefaults() {
  elements.userIdInput.value = state.userId;
  selectMood(state.selectedMood);
  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (browserTimezone) {
    elements.timezoneInput.placeholder = browserTimezone;
  }
}

async function loadApp() {
  await loadTextSources();
  await loadDashboard({ restoreScreen: true });
}

async function loadDashboard({ restoreScreen = false } = {}) {
  const userId = getUserId();
  localStorage.setItem("emmaus.userId", userId);

  const [profile, recommendation, streaks, openItems, latestMood, activeSession] = await Promise.all([
    fetchJson(`/v1/users/${encodeURIComponent(userId)}/profile`),
    fetchJson(`/v1/agent/recommendations/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/engagement/streaks/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/action-items/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/mood/${encodeURIComponent(userId)}`, { allowNull: true }),
    fetchJson(`/v1/agent/session/active/${encodeURIComponent(userId)}`, { allowNull: true }),
  ]);

  state.profile = profile;
  state.recommendation = recommendation;
  state.activeSessionPayload = activeSession;

  renderProfile(profile);
  renderRecommendation(recommendation);
  renderStreaks(streaks);
  renderActionItems(openItems.items || []);
  renderLatestMood(latestMood);
  renderOnboarding(profile, streaks, activeSession);
  renderTodayPlan(recommendation, activeSession, openItems.items || []);
  updateSessionEntryState(activeSession);

  if (activeSession) {
    renderSessionStart(activeSession, { navigate: false });
    localStorage.setItem("emmaus.activeSessionId", activeSession.session.session_id);
  } else {
    clearSessionView();
    localStorage.removeItem("emmaus.activeSessionId");
  }

  await loadNudgeArtifacts();

  if (restoreScreen) {
    restorePreferredScreen();
  }
}

async function loadTextSources() {
  const response = await fetchJson("/v1/sources/text");
  state.textSources = response.sources || response;
  const options = state.textSources
    .map((source) => `<option value="${escapeHtml(source.source_id)}">${escapeHtml(source.name)}</option>`)
    .join("");
  const fallback = '<option value="sample_local">Sample Public Domain Local Source</option>';
  elements.textSourceSelect.innerHTML = options || fallback;
  elements.preferredSourceSelect.innerHTML = options || fallback;
}
function renderProfile(profile) {
  const name = profile.display_name || "friend";
  elements.heroTitle.textContent = `Walk with Christ through Scripture, ${name}.`;
  elements.heroCopy.textContent = "Emmaus guides short, honest sessions that test understanding, surface gaps, and end with a real next step.";
  elements.displayNameInput.value = profile.display_name || "";
  elements.preferredMinutesInput.value = profile.preferences.preferred_session_minutes || 20;
  elements.guideModeSelect.value = profile.preferences.preferred_guide_mode || "guide";
  elements.nudgeIntensitySelect.value = profile.preferences.nudge_intensity || "balanced";
  elements.timezoneInput.value = profile.preferences.timezone === "UTC" ? "" : (profile.preferences.timezone || "");
  elements.studyWindowStartInput.value = profile.preferences.preferred_study_window_start || "";
  elements.studyWindowEndInput.value = profile.preferences.preferred_study_window_end || "";
  elements.quietHoursStartInput.value = profile.preferences.quiet_hours_start || "";
  elements.quietHoursEndInput.value = profile.preferences.quiet_hours_end || "";

  const preferredSource = profile.preferences.preferred_translation_source_id;
  if (preferredSource && Array.from(elements.textSourceSelect.options).some((option) => option.value === preferredSource)) {
    elements.textSourceSelect.value = preferredSource;
    elements.preferredSourceSelect.value = preferredSource;
  }

  state.selectedStudyDays = normalizeStudyDays(profile.preferences.preferred_study_days || []);
  renderStudyDaySelection();
}

function renderStudyDaySelection() {
  elements.studyDaysRow.querySelectorAll(".choice-chip").forEach((chip) => {
    chip.classList.toggle("choice-chip-active", state.selectedStudyDays.includes(chip.dataset.day));
  });
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

function renderOnboarding(profile, streaks, activeSession) {
  const hasConfiguredRhythm = Boolean(profile.display_name) && Boolean(profile.preferences.timezone) && state.selectedStudyDays.length > 0;
  const isNew = (!hasConfiguredRhythm || streaks.completed_sessions === 0) && !activeSession;
  elements.onboardingPanel.classList.toggle("hidden", !isNew);
  if (!isNew) {
    return;
  }

  elements.onboardingCopy.textContent = hasConfiguredRhythm
    ? "Your rhythm is partly set. Finish shaping your schedule or jump into today’s plan."
    : "Start with your name, study days, a preferred window, and your nudge tone. Emmaus will use that rhythm to guide when and how it reaches out.";
}

function renderTodayPlan(recommendation, activeSession, actionItems) {
  const openItems = actionItems.filter((item) => item.status === "open");
  const notificationLine = state.nudgePlan?.fallback_at
    ? `Next notification-safe moment: ${escapeHtml(formatDateTime(state.nudgePlan.fallback_at))}`
    : state.nudgePlan?.deliver_at
      ? `Planned nudge: ${escapeHtml(formatDateTime(state.nudgePlan.deliver_at))}`
      : "Notification timing will adapt to the rhythm you set.";

  if (activeSession) {
    const session = activeSession.session;
    const totalQuestions = session.questions.length;
    const answeredQuestions = session.current_question_index;
    const completion = totalQuestions === 0 ? 0 : Math.round((answeredQuestions / totalQuestions) * 100);
    const nextQuestion = activeSession.current_question ? activeSession.current_question.question : "Complete the session to receive your action step.";
    elements.todayPlanPill.textContent = "In progress";
    elements.heroPrimaryButton.textContent = "Resume Session";
    elements.todayPlanCard.innerHTML = `
      <article class="today-plan-card">
        <div class="recommendation-meta">
          <span class="meta-pill">${escapeHtml(formatReference(session.reference))}</span>
          <span class="meta-pill">${escapeHtml(session.guide_mode)}</span>
          <span class="meta-pill">${escapeHtml(`${session.requested_minutes} min`)}</span>
        </div>
        <h3>Keep going with the session you already started.</h3>
        <p class="today-plan-copy">${escapeHtml(session.latest_message)}</p>
        <div class="progress-track"><div class="progress-fill" style="width: ${completion}%"></div></div>
        <p class="micro-copy">${answeredQuestions} of ${totalQuestions} questions answered. Next: ${escapeHtml(nextQuestion)}</p>
        <p class="micro-copy">${notificationLine}</p>
        <div class="today-plan-actions">
          <button class="primary-button" type="button" data-action="resume-session">Resume session</button>
          <button class="secondary-button" type="button" data-action="open-actions">Action items</button>
        </div>
      </article>
    `;
    return;
  }

  const nextAction = openItems[0]?.title || recommendation.suggested_action;
  elements.todayPlanPill.textContent = openItems.length > 0 ? "Follow through" : "Ready";
  elements.heroPrimaryButton.textContent = openItems.length > 0 ? "Open Action Item" : "Start Today's Plan";
  elements.todayPlanCard.innerHTML = `
    <article class="today-plan-card">
      <div class="recommendation-meta">
        <span class="meta-pill">${escapeHtml(formatReference(recommendation.recommended_reference))}</span>
        <span class="meta-pill">${escapeHtml(recommendation.recommended_guide_mode)}</span>
        <span class="meta-pill">${escapeHtml(`${recommendation.recommended_minutes} min`)}</span>
      </div>
      <h3>${openItems.length > 0 ? "Your next step is still waiting." : "Today’s plan is ready."}</h3>
      <p class="today-plan-copy">${escapeHtml(openItems.length > 0 ? openItems[0].detail : recommendation.reason)}</p>
      <p class="micro-copy">${openItems.length > 0 ? `Follow through on: ${escapeHtml(nextAction)}` : `Start from “${escapeHtml(recommendation.recommended_entry_point)}” and end by acting on: ${escapeHtml(nextAction)}`}</p>
      <p class="micro-copy">${notificationLine}</p>
      <div class="today-plan-actions">
        <button class="primary-button" type="button" data-action="${openItems.length > 0 ? "open-actions" : "start-today-plan"}">${openItems.length > 0 ? "Open action item" : "Start today’s plan"}</button>
        <button class="secondary-button" type="button" data-action="open-study">Review session setup</button>
      </div>
    </article>
  `;
}

function renderActionItems(items) {
  const openCount = items.filter((item) => item.status === "open").length;
  elements.openActionCount.textContent = String(openCount);
  elements.openActionCopy.textContent = openCount > 0
    ? items.find((item) => item.status === "open")?.title || "Your next step is ready."
    : "Your next step will show up here.";
  elements.actionSummaryPill.textContent = `${openCount} open`;

  if (!items.length) {
    elements.actionItemList.innerHTML = '<p class="empty-state">No action items yet. Finish a session and Emmaus will turn it into a practical step.</p>';
    renderActionFollowUpSelection(null, items);
    return;
  }

  elements.actionItemList.innerHTML = items.map((item) => `
    <article class="action-card ${item.status === "completed" ? "completed" : ""}">
      <div class="action-card-header">
        <div>
          <p class="panel-label">${escapeHtml(item.status)}</p>
          <h3>${escapeHtml(item.title)}</h3>
        </div>
        ${item.status === "open" ? `<button class="action-button" type="button" data-action="select-follow-up" data-id="${escapeHtml(item.action_item_id)}">Reflect and complete</button>` : `<span class="meta-pill">${escapeHtml(item.follow_up_outcome || "completed")}</span>`}
      </div>
      <p>${escapeHtml(item.detail)}</p>
      ${item.follow_up_note ? `<p class="micro-copy">Follow-up: ${escapeHtml(item.follow_up_note)}</p>` : `<p class="micro-copy">Created ${escapeHtml(formatDate(item.created_at))}</p>`}
    </article>
  `).join("");

  const selected = items.find((item) => item.action_item_id === state.selectedActionItemId && item.status === "open");
  renderActionFollowUpSelection(selected || items.find((item) => item.status === "open") || null, items);
}

function renderActionFollowUpSelection(item, items = []) {
  if (!item) {
    state.selectedActionItemId = null;
    elements.followUpTargetCopy.textContent = items.some((entry) => entry.status === "open")
      ? "Select an open action item above to complete it with a short reflection."
      : "No open action items right now. Finish a session and Emmaus will surface your next step here.";
    elements.followUpSubmitButton.disabled = true;
    elements.followUpNoteInput.value = "";
    return;
  }

  state.selectedActionItemId = item.action_item_id;
  elements.followUpTargetCopy.textContent = `Following through on: ${item.title}`;
  elements.followUpSubmitButton.disabled = false;
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

async function loadNudgeArtifacts(previewAt = null) {
  const payload = { user_id: getUserId() };
  if (previewAt) {
    payload.preview_at = previewAt;
  }

  const [nudge, nudgePlan] = await Promise.all([
    fetchJson("/v1/agent/nudges/preview", { method: "POST", body: JSON.stringify(payload) }),
    fetchJson("/v1/agent/nudges/plan", { method: "POST", body: JSON.stringify(payload) }),
  ]);
  state.nudge = nudge;
  state.nudgePlan = nudgePlan;
  renderNudge(nudge, nudgePlan);
}

function renderNudge(nudge, plan) {
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

  elements.nudgePlanCard.innerHTML = `
    <article class="nudge-plan-card">
      <p class="panel-label">Delivery plan</p>
      <h3>${escapeHtml(formatDeliveryStatus(plan.delivery_status))}</h3>
      <p>${escapeHtml(plan.reason)}</p>
      <div class="recommendation-meta">
        <span class="meta-pill">${escapeHtml(plan.delivery_channel)}</span>
        <span class="meta-pill">${escapeHtml(plan.idempotency_key)}</span>
      </div>
      <p class="micro-copy">${plan.deliver_at ? `Deliver at ${escapeHtml(formatDateTime(plan.deliver_at))}` : "No push send is planned right now."}${plan.fallback_at ? ` Fallback: ${escapeHtml(formatDateTime(plan.fallback_at))}` : ""}</p>
    </article>
  `;
}
function updateSessionEntryState(activeSession) {
  const disabled = Boolean(activeSession);
  elements.sessionFormButton.disabled = disabled;
  elements.entryPointInput.disabled = disabled;
  elements.requestedMinutesInput.disabled = disabled;
  elements.sessionGuideMode.disabled = disabled;
  elements.textSourceSelect.disabled = disabled;
  elements.sessionFormCopy.textContent = disabled
    ? "You already have a session in progress. Resume it below or finish it before starting a new one."
    : "Start a fresh guided session when you are ready.";
  elements.sessionFormButton.textContent = disabled ? "Session in progress" : "Begin guided session";
}

function renderSessionStart(payload, options = {}) {
  const { navigate = true } = options;
  state.activeSessionPayload = payload;
  state.currentQuestion = payload.current_question;
  localStorage.setItem("emmaus.activeSessionId", payload.session.session_id);

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
  if (navigate) {
    showScreen("session");
  }
}

function renderCurrentQuestion(question, totalQuestions, currentIndex) {
  state.currentQuestion = question;
  const visibleProgress = question ? currentIndex + 1 : totalQuestions;
  elements.questionProgressPill.textContent = `${visibleProgress} / ${totalQuestions}`;
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
  state.activeSessionPayload = { ...state.activeSessionPayload, session: payload.session, current_question: payload.next_question };
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
  state.activeSessionPayload = null;
  state.currentQuestion = null;
  localStorage.removeItem("emmaus.activeSessionId");

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
  updateSessionEntryState(null);
  showToast("Session completed. Your action step is ready.");
  loadDashboard({ restoreScreen: false }).catch(handleError);
  showScreen("actions");
}

function clearSessionView() {
  state.activeSessionPayload = null;
  state.currentQuestion = null;
  elements.sessionStatusPill.textContent = "Ready";
  elements.sessionReference.textContent = "No active session yet";
  elements.questionProgressPill.textContent = "0 / 0";
  elements.sessionHero.innerHTML = '<article class="inline-card"><p>Emmaus will keep your place here when you return.</p></article>';
  elements.passageText.textContent = "Start a session to see the passage, plan, and first question.";
  elements.sessionPlan.innerHTML = "";
  elements.commentaryBlock.innerHTML = "";
  elements.currentQuestionHeading.textContent = "Current question";
  elements.currentQuestionCopy.textContent = "Emmaus will place the next question here.";
  elements.responseText.value = "";
  elements.responseText.disabled = false;
  elements.submitResponseButton.disabled = false;
}

function restorePreferredScreen() {
  const preferred = localStorage.getItem("emmaus.activeScreen") || "home";
  if (preferred === "session" && state.activeSessionPayload) {
    showScreen("session");
    return;
  }
  showScreen(preferred);
}

function showScreen(screenName) {
  state.activeScreen = screenName;
  localStorage.setItem("emmaus.activeScreen", screenName);
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

function toggleStudyDay(day) {
  if (state.selectedStudyDays.includes(day)) {
    state.selectedStudyDays = state.selectedStudyDays.filter((entry) => entry !== day);
  } else {
    state.selectedStudyDays = [...state.selectedStudyDays, day];
  }
  renderStudyDaySelection();
}

async function onHeroPrimaryAction() {
  const openItems = await fetchJson(`/v1/study/action-items/${encodeURIComponent(getUserId())}?status=open`);
  if (state.activeSessionPayload) {
    showScreen("session");
    return;
  }
  if (openItems.items?.length) {
    showScreen("actions");
    return;
  }
  await startRecommendedSession();
}

async function onTodayPlanAction(event) {
  const button = event.target.closest("[data-action]");
  if (!button) {
    return;
  }
  const action = button.dataset.action;
  if (action === "resume-session") {
    showScreen("session");
    return;
  }
  if (action === "open-actions") {
    showScreen("actions");
    return;
  }
  if (action === "open-study") {
    showScreen("session");
    return;
  }
  if (action === "start-today-plan") {
    await startRecommendedSession();
  }
}

async function onOnboardingAction(event) {
  const button = event.target.closest("[data-action]");
  if (!button) {
    return;
  }
  const action = button.dataset.action;
  if (action === "focus-identity") {
    elements.displayNameInput.focus();
    return;
  }
  if (action === "start-today-plan") {
    await startRecommendedSession();
  }
}

async function startRecommendedSession() {
  const payload = {
    user_id: getUserId(),
    display_name: elements.displayNameInput.value.trim() || null,
    text_source_id: elements.textSourceSelect.value || elements.preferredSourceSelect.value || null,
    entry_point: state.recommendation?.recommended_entry_point || elements.entryPointInput.value.trim() || "continue where I left off",
    requested_minutes: state.recommendation?.recommended_minutes || numberOrNull(elements.requestedMinutesInput.value),
    guide_mode: null,
  };

  const session = await fetchJson("/v1/agent/session/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderSessionStart(session);
  updateSessionEntryState(session);
  showToast("Session started.");
  await loadDashboard({ restoreScreen: false });
  showScreen("session");
}
async function onSaveIdentity(event) {
  event.preventDefault();
  const userId = getUserId();
  const payload = {
    display_name: elements.displayNameInput.value.trim() || null,
    preferred_session_minutes: numberOrNull(elements.preferredMinutesInput.value),
    preferred_guide_mode: elements.guideModeSelect.value || null,
    preferred_translation_source_id: elements.preferredSourceSelect.value || null,
    nudge_intensity: elements.nudgeIntensitySelect.value || null,
    timezone: elements.timezoneInput.value.trim() || Intl.DateTimeFormat().resolvedOptions().timeZone || null,
    preferred_study_days: state.selectedStudyDays,
    preferred_study_window_start: elements.studyWindowStartInput.value || null,
    preferred_study_window_end: elements.studyWindowEndInput.value || null,
    quiet_hours_start: elements.quietHoursStartInput.value || null,
    quiet_hours_end: elements.quietHoursEndInput.value || null,
  };

  const profile = await fetchJson(`/v1/users/${encodeURIComponent(userId)}/preferences`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  state.profile = profile;
  renderProfile(profile);
  showToast("Guide preferences saved.");
  await loadDashboard({ restoreScreen: false });
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
  await loadDashboard({ restoreScreen: false });
}

async function onStartSession(event) {
  event.preventDefault();
  if (state.activeSessionPayload) {
    showToast("Resume or finish your current session before starting another.");
    showScreen("session");
    return;
  }

  const payload = {
    user_id: getUserId(),
    display_name: elements.displayNameInput.value.trim() || null,
    text_source_id: elements.textSourceSelect.value || elements.preferredSourceSelect.value || null,
    entry_point: elements.entryPointInput.value.trim() || "continue where I left off",
    requested_minutes: numberOrNull(elements.requestedMinutesInput.value),
    guide_mode: elements.sessionGuideMode.value || null,
  };

  const session = await fetchJson("/v1/agent/session/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderSessionStart(session);
  updateSessionEntryState(session);
  showToast("Session started.");
  await loadDashboard({ restoreScreen: false });
}

async function onSubmitResponse(event) {
  event.preventDefault();
  if (!state.activeSessionPayload || !state.currentQuestion) {
    showToast("Start or resume a session first.");
    return;
  }

  const text = elements.responseText.value.trim();
  if (!text) {
    showToast("Write a response before sending it.");
    return;
  }

  const payload = {
    session_id: state.activeSessionPayload.session.session_id,
    user_id: getUserId(),
    response_text: text,
    engagement_score: Number(elements.engagementInput.value || 4),
  };

  const turn = await fetchJson("/v1/agent/session/respond", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderSessionTurn(turn);
  await loadDashboard({ restoreScreen: false });
}

async function onCompleteSession(event) {
  event.preventDefault();
  if (!state.activeSessionPayload) {
    showToast("Start or resume a session first.");
    return;
  }

  const payload = {
    session_id: state.activeSessionPayload.session.session_id,
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
  const button = event.target.closest("[data-action='select-follow-up']");
  if (!button) {
    return;
  }
  state.selectedActionItemId = button.dataset.id;
  const items = await fetchJson(`/v1/study/action-items/${encodeURIComponent(getUserId())}`);
  renderActionItems(items.items || []);
  showScreen("actions");
}

async function onSubmitActionFollowUp(event) {
  event.preventDefault();
  if (!state.selectedActionItemId) {
    showToast("Select an action item first.");
    return;
  }

  const payload = {
    user_id: getUserId(),
    follow_up_note: elements.followUpNoteInput.value.trim() || null,
    follow_up_outcome: elements.followUpOutcomeSelect.value || null,
  };

  await fetchJson(`/v1/study/action-items/${encodeURIComponent(state.selectedActionItemId)}/complete`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  showToast("Follow-through saved.");
  elements.followUpNoteInput.value = "";
  state.selectedActionItemId = null;
  await loadDashboard({ restoreScreen: false });
}

async function onPreviewNudgeAtTime(event) {
  event.preventDefault();
  const previewValue = elements.previewAtInput.value;
  const previewAt = previewValue ? new Date(previewValue).toISOString() : null;
  await loadNudgeArtifacts(previewAt);
  showToast("Nudge timing refreshed.");
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

function normalizeStudyDays(days) {
  return (days || []).map((day) => day.slice(0, 3).toLowerCase());
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

function formatDeliveryStatus(status) {
  if (status === "scheduled") {
    return "Scheduled for later";
  }
  if (status === "suppressed") {
    return "Hold push notification";
  }
  return "Ready to send";
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
