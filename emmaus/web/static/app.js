const STARTER_SOURCE_ID = "sample_local";
const ESV_SOURCE_ID = "esv";
const DEFAULT_TEXT_SOURCES = [
  { source_id: STARTER_SOURCE_ID, name: "Included Starter Bible" },
  { source_id: "user_api_placeholder", name: "User API Placeholder" },
];
const DEFAULT_TRANSLATION_TEMPLATES = [
  { template_id: "starter", name: "Included Starter Bible", setup_mode: "starter", description: "Begin immediately with the Bible already included in Emmaus.", recommended: true, source_id: STARTER_SOURCE_ID },
  { template_id: "esv", name: "ESV", setup_mode: "esv_api", description: "Connect the official ESV API with your Crossway API key.", recommended: false, source_id: ESV_SOURCE_ID },
  { template_id: "web", name: "WEB", setup_mode: "upload", description: "Upload a WEB JSON file from this device.", recommended: false, source_id: null },
  { template_id: "kjv", name: "KJV", setup_mode: "upload", description: "Upload a KJV JSON file or connect the source you already use.", recommended: false, source_id: null },
  { template_id: "asv", name: "ASV", setup_mode: "upload", description: "Upload an ASV JSON file from this device.", recommended: false, source_id: null },
  { template_id: "licensed_other", name: "Other licensed translation", setup_mode: "generic_api", description: "Connect another licensed provider such as NIV, NLT, NKJV, NASB, or CSB.", recommended: false, source_id: null },
];

const DEMO_SCENARIO_LABELS = {
  live: "Live data",
  first_visit: "First visit",
  comprehension_gap: "Comprehension gap",
  in_progress: "In progress session",
  overdue_action: "Overdue next step",
  scheduled_nudge: "Scheduled nudge",
};

const DEMO_SCENARIO_DETAILS = {
  live: "You are viewing your real Emmaus profile, current session, and next steps.",
  first_visit: "Shows how Emmaus feels for a brand-new user starting gently for the first time.",
  comprehension_gap: "Shows a slower session where Emmaus helps the user stay closer to the passage before applying it.",
  in_progress: "Shows an active session already underway so you can preview the resume experience.",
  overdue_action: "Shows a user with an unfinished next step so the Home and Actions flow can focus on follow-through.",
  scheduled_nudge: "Shows how Emmaus previews a comeback reminder when it is time to re-engage the user.",
};

const state = {
  userId: localStorage.getItem("emmaus.userId") || "demo-user",
  activeScreen: localStorage.getItem("emmaus.activeScreen") || "home",
  demoScenario: getInitialDemoScenario(),
  selectedMood: "neutral",
  selectedStudyDays: [],
  selectedActionItemId: null,
  activeSessionPayload: null,
  currentQuestion: null,
  recommendation: null,
  nudge: null,
  nudgePlan: null,
  profile: null,
  streaks: null,
  memorySummary: null,
  lastCompletion: null,
  lastFollowThroughUpdate: null,
  actionItems: [],
  prayerItems: [],
  reviewHistory: null,
  onboardingStep: 1,
  textSources: [],
  translationTemplates: [],
  sourcePreview: null,
  bibleManagerExpanded: false,
  bibleSetupExpanded: false,
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
    demoSceneRow: document.getElementById("demo-scene-row"),
    demoStatusCopy: document.getElementById("demo-status-copy"),
    demoSceneDetail: document.getElementById("demo-scene-detail"),
    onboardingPanel: document.getElementById("onboarding-panel"),
    onboardingCopy: document.getElementById("onboarding-copy"),
    onboardingStepPill: document.getElementById("onboarding-step-pill"),
    onboardingFlow: document.getElementById("onboarding-flow"),
    todayPlanPill: document.getElementById("today-plan-pill"),
    todayPlanCard: document.getElementById("today-plan-card"),
    memoryThreadPill: document.getElementById("memory-thread-pill"),
    memoryThreadCard: document.getElementById("memory-thread-card"),
    sourceCurrentName: document.getElementById("source-current-name"),
    sourceCurrentDetail: document.getElementById("source-current-detail"),
    sourceManageToggle: document.getElementById("source-manage-toggle"),
    sourceManagerDetails: document.getElementById("source-manager-details"),
    sourcePreviewCard: document.getElementById("source-preview-card"),
    homeBibleCurrentName: document.getElementById("home-bible-current-name"),
    openBibleSettingsButton: document.getElementById("open-bible-settings-button"),
    profileBiblePanel: document.getElementById("profile-bible-panel"),
    identityForm: document.getElementById("identity-form"),
    userIdInput: document.getElementById("user-id-input"),
    displayNameInput: document.getElementById("display-name-input"),
    preferredMinutesInput: document.getElementById("preferred-minutes-input"),
    guideModeSelect: document.getElementById("guide-mode-select"),
    questionStyleSelect: document.getElementById("question-style-select"),
    guidanceToneSelect: document.getElementById("guidance-tone-select"),
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
    lookBackPill: document.getElementById("look-back-pill"),
    lookBackCard: document.getElementById("look-back-card"),
    lookBackForm: document.getElementById("look-back-form"),
    lookBackResponseText: document.getElementById("look-back-response-text"),
    moodForm: document.getElementById("mood-form"),
    moodChipRow: document.getElementById("mood-chip-row"),
    energySelect: document.getElementById("energy-select"),
    moodNotes: document.getElementById("mood-notes"),
    latestMoodCopy: document.getElementById("latest-mood-copy"),
    sessionForm: document.getElementById("session-form"),
    sessionFormCopy: document.getElementById("session-form-copy"),
    sessionFormButton: document.getElementById("session-form-button"),
    sessionPanelHeading: document.getElementById("session-panel-heading"),
    entryPointInput: document.getElementById("entry-point-input"),
    requestedMinutesInput: document.getElementById("requested-minutes-input"),
    sessionGuideMode: document.getElementById("session-guide-mode"),
    textSourceSelect: document.getElementById("text-source-select"),
    sessionStatusPill: document.getElementById("session-status-pill"),
    sessionReference: document.getElementById("session-reference"),
    passageReference: document.getElementById("passage-reference"),
    questionProgressPill: document.getElementById("question-progress-pill"),
    sessionHero: document.getElementById("session-hero"),
    passageText: document.getElementById("passage-text"),
    sessionPlan: document.getElementById("session-plan"),
    commentaryBlock: document.getElementById("commentary-block"),
    currentQuestionHeading: document.getElementById("current-question-heading"),
    questionTransitionCopy: document.getElementById("question-transition-copy"),
    currentQuestionCopy: document.getElementById("current-question-copy"),
    responseForm: document.getElementById("response-form"),
    responseText: document.getElementById("response-text"),
    engagementInput: document.getElementById("engagement-input"),
    submitResponseButton: document.getElementById("submit-response-button"),
    completeForm: document.getElementById("complete-form"),
    summaryNotes: document.getElementById("summary-notes"),
    actionItemTitle: document.getElementById("action-item-title"),
    actionItemDetail: document.getElementById("action-item-detail"),
    completionSummaryPill: document.getElementById("completion-summary-pill"),
    completionSummaryCard: document.getElementById("completion-summary-card"),
    actionSummaryPill: document.getElementById("action-summary-pill"),
    actionItemList: document.getElementById("action-item-list"),
    prayerSummaryPill: document.getElementById("prayer-summary-pill"),
    prayerItemList: document.getElementById("prayer-item-list"),
    reviewSummaryPill: document.getElementById("review-summary-pill"),
    reviewHistoryCard: document.getElementById("review-history-card"),
    prayerForm: document.getElementById("prayer-form"),
    prayerTitleInput: document.getElementById("prayer-title-input"),
    prayerDetailInput: document.getElementById("prayer-detail-input"),
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
  elements.sourceManageToggle?.addEventListener("click", onToggleBibleManager);
  elements.openBibleSettingsButton?.addEventListener("click", openBibleSettingsInProfile);
  elements.navButtons.forEach((button) => {
    button.addEventListener("click", () => showScreen(button.dataset.navTarget));
  });
  bindMemorizeEvents();
  bindStudyNotesEvents();
  elements.demoSceneRow.addEventListener("click", reportFailures(onDemoScenarioSelect));
  elements.refreshButton?.addEventListener("click", reportFailures(onRefreshClick));
  elements.heroPrimaryButton.addEventListener("click", reportFailures(onHeroPrimaryAction));
  elements.previewNudgeButton.addEventListener("click", () => {
    showScreen("nudges");
    loadNudgeArtifacts().catch(handleError);
  });
  elements.identityForm.addEventListener("submit", reportFailures(onSaveIdentity));
  elements.moodForm.addEventListener("submit", reportFailures(onSaveMood));
  elements.lookBackForm?.addEventListener("submit", reportFailures(onSubmitLookBack));
  elements.sessionForm.addEventListener("submit", reportFailures(onStartSession));
  elements.responseForm.addEventListener("submit", reportFailures(onSubmitResponse));
  elements.completeForm.addEventListener("submit", reportFailures(onCompleteSession));
  elements.actionFollowUpForm.addEventListener("submit", reportFailures(onSubmitActionFollowUp));
  elements.nudgePreviewForm.addEventListener("submit", reportFailures(onPreviewNudgeAtTime));
  elements.todayPlanCard.addEventListener("click", reportFailures(onTodayPlanAction));
  elements.onboardingPanel.addEventListener("click", reportFailures(onOnboardingAction));
  elements.actionItemList.addEventListener("click", onActionListClick);
  elements.prayerItemList?.addEventListener("click", reportFailures(onPrayerListClick));
  elements.sessionHero?.addEventListener("click", reportFailures(onPrayerListClick));
  elements.prayerForm?.addEventListener("submit", reportFailures(onSubmitPrayerItem));
  elements.moodChipRow.querySelectorAll(".choice-chip").forEach((chip) => chip.addEventListener("click", () => selectMood(chip.dataset.value)));
  elements.studyDaysRow.querySelectorAll(".choice-chip").forEach((chip) => chip.addEventListener("click", () => toggleStudyDay(chip.dataset.day)));
  bindActionFieldTabFill();
}

const reportingHandlers = new WeakMap();

// Returns one stable wrapper per handler so re-binding stays de-duplicated by addEventListener.
function reportFailures(handler) {
  if (!reportingHandlers.has(handler)) {
    reportingHandlers.set(handler, (event) => {
      try {
        const result = handler(event);
        if (result && typeof result.catch === "function") {
          result.catch(handleError);
        }
      } catch (error) {
        handleError(error);
      }
    });
  }
  return reportingHandlers.get(handler);
}

function bindActionFieldTabFill() {
  [
    elements.responseText,
    elements.summaryNotes,
    elements.actionItemTitle,
    elements.actionItemDetail,
    elements.prayerTitleInput,
    elements.prayerDetailInput,
    elements.followUpNoteInput,
  ].filter(Boolean).forEach((field) => {
    field.addEventListener("keydown", onActionFieldTabFill);
  });
}

function onActionFieldTabFill(event) {
  if (event.key !== "Tab" || event.shiftKey || event.altKey || event.ctrlKey || event.metaKey) {
    return;
  }

  const field = event.currentTarget;
  const placeholder = optionalText(field?.getAttribute("placeholder"));
  const currentValue = optionalText(field?.value);
  if (!placeholder || currentValue) {
    return;
  }

  event.preventDefault();
  field.value = placeholder;
  field.dispatchEvent(new Event("input", { bubbles: true }));
  field.dispatchEvent(new Event("change", { bubbles: true }));

  const caretPosition = field.value.length;
  if (typeof field.setSelectionRange === "function") {
    field.setSelectionRange(caretPosition, caretPosition);
  }
}
async function onRefreshClick() {
  const originalLabel = elements.refreshButton.textContent;
  elements.refreshButton.disabled = true;
  elements.refreshButton.textContent = "Refreshing...";
  try {
    await refreshExperience({ restoreScreen: false });
    showToast("Emmaus refreshed your current view.");
  } catch (error) {
    handleError(error);
  } finally {
    elements.refreshButton.disabled = false;
    elements.refreshButton.textContent = originalLabel;
  }
}

function initializeDefaults() {
  elements.userIdInput.value = state.userId;
  state.onboardingStep = getStoredOnboardingStep();
  selectMood(state.selectedMood);
  if (elements.timezoneInput && !elements.timezoneInput.value) {
    elements.timezoneInput.value = "America/New_York";
  }
  renderDemoControls();
}

async function loadApp() {
  await loadTranslationTemplates();
  await loadTextSources();
  await refreshExperience({ restoreScreen: true });
}

async function loadTranslationTemplates() {
  if (isDemoMode()) {
    state.translationTemplates = DEFAULT_TRANSLATION_TEMPLATES;
    return;
  }
  try {
    const response = await fetchJson("/v1/sources/text/templates");
    state.translationTemplates = response.items || DEFAULT_TRANSLATION_TEMPLATES;
  } catch {
    state.translationTemplates = DEFAULT_TRANSLATION_TEMPLATES;
  }
}

async function refreshExperience({ restoreScreen = false } = {}) {
  if (isDemoMode()) {
    renderDemoDashboard({ restoreScreen });
    return;
  }
  await loadLiveDashboard({ restoreScreen });
}

function getSourceById(sourceId) {
  const sources = state.textSources.length ? state.textSources : DEFAULT_TEXT_SOURCES;
  return sources.find((source) => source.source_id === sourceId) || null;
}

function getEffectivePreferredSourceId(sources) {
  const explicitPreference = state.profile?.preferences?.preferred_translation_source_id || elements.preferredSourceSelect?.value || "";
  if (explicitPreference) {
    return explicitPreference;
  }
  if (sources.some((source) => source.source_id === ESV_SOURCE_ID)) {
    return ESV_SOURCE_ID;
  }
  return sources[0]?.source_id || "";
}

function buildPassageMarkup(passage) {
  if (!passage?.text) {
    return "Start a session to see the passage, plan, and first question.";
  }

  const passageBody = escapeHtml(passage.text).replace(/\n/g, "<br />");
  const notice = passage.copyright_notice
    ? `<p class="passage-notice">${escapeHtml(passage.copyright_notice)}</p>`
    : "";
  return `${passageBody}${notice}`;
}

function renderTextSourceOptions() {
  const sources = state.textSources.length ? state.textSources : DEFAULT_TEXT_SOURCES;
  const options = sources
    .map((source) => `<option value="${escapeHtml(source.source_id)}">${escapeHtml(source.name)}</option>`)
    .join("");

  if (elements.textSourceSelect) {
    elements.textSourceSelect.innerHTML = options;
  }
  if (elements.preferredSourceSelect) {
    elements.preferredSourceSelect.innerHTML = options;
  }

  const preferredSourceId = getEffectivePreferredSourceId(sources);
  const activeSessionSourceId = state.activeSessionPayload?.session?.text_source_id || "";
  const sessionSourceId = activeSessionSourceId || preferredSourceId;

  if (preferredSourceId && elements.preferredSourceSelect) {
    elements.preferredSourceSelect.value = preferredSourceId;
  }
  if (sessionSourceId && elements.textSourceSelect) {
    elements.textSourceSelect.value = sessionSourceId;
  }

  renderBibleSourceManager();
}

function getInitialDemoScenario() {
  const params = new URLSearchParams(window.location.search);
  const fromUrl = normalizeDemoScenario(params.get("demo"));
  if (fromUrl) {
    localStorage.setItem("emmaus.demoScenario", fromUrl);
    return fromUrl;
  }
  return "live";
}

function normalizeDemoScenario(value) {
  if (!value) {
    return null;
  }
  return DEMO_SCENARIO_LABELS[value] ? value : null;
}

function isDemoMode() {
  return state.demoScenario !== "live";
}

function buildDemoScenarioData(scenario) {
  const baseProfile = {
    user_id: "demo-user",
    display_name: "Brian",
    preferences: {
      preferred_translation_source_id: STARTER_SOURCE_ID,
      preferred_difficulty: "balanced",
      preferred_session_minutes: 15,
      preferred_guide_mode: "coach",
      nudge_intensity: "balanced",
      preferred_study_days: ["mon", "wed", "fri"],
      timezone: "America/New_York",
      preferred_study_window_start: "07:30",
      preferred_study_window_end: "08:15",
      quiet_hours_start: "21:00",
      quiet_hours_end: "06:30",
    },
    completed_sessions: 6,
    current_streak: 3,
    longest_streak: 6,
    last_completed_on: "2026-04-04",
  };

  const baseRecommendation = {
    user_id: "demo-user",
    focus_area: "application",
    recommended_reference: { book: "John", chapter: 3, start_verse: 16, end_verse: 17 },
    recommended_guide_mode: "coach",
    recommended_minutes: 15,
    recommended_entry_point: "continue where I left off",
    reason: "Recent study is strong, but Emmaus wants to push the next session toward clearer follow-through.",
    suggested_action: "Name one person to encourage or one concrete act of obedience before the day ends.",
    gap_report: {
      user_id: "demo-user",
      comprehension_gap: 0.28,
      application_gap: 0.68,
      consistency_gap: 0.24,
      focus_area: "application",
      observed_patterns: [
        "Application responses have been sincere but not always specific.",
        "Open next steps suggest follow-through needs a little reinforcement.",
      ],
    },
  };

  const baseMemorySummary = {
    user_id: "demo-user",
    latest_summary: "Emmaus has been tracing how Christ moves toward discouraged people and calling the user to respond with concrete encouragement.",
    recurring_themes: ["Christ's initiating love", "encouraging discouraged people"],
    growth_areas: ["turning reflection into same-day obedience", "slowing down long enough to notice what the text says first"],
    carry_forward_prompt: "Return to Christ's initiating love and take one concrete step of encouragement before moving on to a new thread.",
    recent_references: ["John 3:16-17", "Luke 24:13-17"],
    memory_count: 3,
  };

  const firstVisitMemorySummary = {
    user_id: "demo-user",
    latest_summary: null,
    recurring_themes: [],
    growth_areas: [],
    carry_forward_prompt: null,
    recent_references: [],
    memory_count: 0,
  };

  const firstVisitProfile = {
    ...baseProfile,
    display_name: null,
    preferences: {
      ...baseProfile.preferences,
      preferred_translation_source_id: null,
      preferred_guide_mode: "guide",
      nudge_intensity: "gentle",
      preferred_study_days: [],
      timezone: "UTC",
      preferred_study_window_start: null,
      preferred_study_window_end: null,
    },
    completed_sessions: 0,
    current_streak: 0,
    longest_streak: 0,
    last_completed_on: null,
  };

  const activeSession = {
    session: {
      session_id: "demo-session-01",
      user_id: "demo-user",
      status: "active",
      entry_point: "continue where I left off",
      guide_mode: "coach",
      requested_minutes: 15,
      text_source_id: STARTER_SOURCE_ID,
      commentary_source_id: "notes_placeholder",
      llm_source_id: "local_rules",
      reference: { book: "John", chapter: 3, start_verse: 16, end_verse: 17 },
      questions: [
        { question: "What in this passage is easiest to admire but hardest to obey?", type: "observation", difficulty: "balanced" },
        { question: "What does this passage reveal about God's character or intentions?", type: "interpretation", difficulty: "balanced" },
        { question: "What is one clear next step you will follow through on before your next session?", type: "application", difficulty: "balanced" },
      ],
      plan: [
        { title: "Read Slowly", instruction: "Read John 3:16-17 twice and notice the direction of God's love.", estimated_minutes: 4 },
        { title: "Focus", instruction: "Pay attention to what the passage says God does before you think about your own response.", estimated_minutes: 3 },
        { title: "Reflect", instruction: "Answer the guide's questions with clear, concrete responses.", estimated_minutes: 5 },
        { title: "Respond", instruction: "Name one practical act of love or courage for today.", estimated_minutes: 3 },
      ],
      started_at: "2026-04-05T07:40:00-04:00",
      completed_at: null,
      current_question_index: 1,
      latest_message: "You named the tension well. Stay close to the text and let it clarify what God is doing before you jump to application.",
      action_item_id: null,
    },
    passage: {
      source_id: STARTER_SOURCE_ID,
      translation_name: "Included Starter Bible",
      reference: { book: "John", chapter: 3, start_verse: 16, end_verse: 17 },
      text: "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life. For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
      copyright_notice: "Public Domain",
    },
    commentary: [
      {
        source_id: "notes_placeholder",
        title: "Commentary Placeholder",
        body: "In demo mode, this note stands in for a modular commentary source that helps the reader slow down around the text.",
        reference: { book: "John", chapter: 3, start_verse: 16, end_verse: 17 },
        metadata: {},
      },
    ],
    pattern_summary: {
      user_id: "demo-user",
      average_engagement: 4.1,
      preferred_difficulty: "balanced",
      recent_topics: ["John 3", "Psalm 23", "Romans 8"],
      recommended_session_minutes: 15,
    },
    recommendation: baseRecommendation,
    current_question: { question: "What does this passage reveal about God's character or intentions?", type: "interpretation", difficulty: "balanced" },
  };

  const completedActionHistory = [
    {
      action_item_id: "demo-action-archived-01",
      user_id: "demo-user",
      session_id: "demo-session-archived-01",
      title: "Pray with Sarah after group",
      detail: "Ask Sarah how she is really doing and pray with her before heading home.",
      status: "completed",
      created_at: "2026-04-01T19:10:00-04:00",
      completed_at: "2026-04-01T21:05:00-04:00",
      follow_up_note: "I almost left without doing it, but the conversation opened naturally and we prayed together in the parking lot.",
      follow_up_outcome: "prayed_through",
    },
    {
      action_item_id: "demo-action-archived-02",
      user_id: "demo-user",
      session_id: "demo-session-archived-02",
      title: "Share Psalm 23 with Dad",
      detail: "Call Dad on the drive home and tell him why Psalm 23 steadied you this week.",
      status: "completed",
      created_at: "2026-04-02T07:15:00-04:00",
      completed_at: "2026-04-02T18:42:00-04:00",
      follow_up_note: "The call was shorter than I hoped, but I still shared the verse and asked how I could keep praying for him.",
      follow_up_outcome: "discussed_with_someone",
    },
  ];

  const overdueActionItems = [
    {
      action_item_id: "demo-action-01",
      user_id: "demo-user",
      session_id: "demo-session-previous",
      title: "Text Mark before lunch",
      detail: "Send one message of encouragement to Mark and offer to pray for whatever he is carrying this week.",
      status: "open",
      created_at: "2026-04-03T08:15:00-04:00",
      completed_at: null,
      follow_up_note: null,
      follow_up_outcome: null,
    },
    ...completedActionHistory,
  ];

  const scheduledActionHistory = [
    ...completedActionHistory,
    {
      action_item_id: "demo-action-archived-03",
      user_id: "demo-user",
      session_id: "demo-session-archived-03",
      title: "Write one sentence of gratitude before bed",
      detail: "End the day by writing one line about where you saw Christ's faithfulness.",
      status: "completed",
      created_at: "2026-04-04T20:55:00-04:00",
      completed_at: "2026-04-04T22:08:00-04:00",
      follow_up_note: "It was brief, but it helped me end the day with more clarity and less hurry.",
      follow_up_outcome: "completed",
    },
  ];

  const scheduledNudge = {
    user_id: "demo-user",
    nudge_type: "theme",
    title: "Build on what already landed",
    message: "You already followed through on 'Write one sentence of gratitude before bed.' Build on the completed step 'Write one sentence of gratitude before bed' and ask what fresh obedience Christ is inviting next.",
    recommended_entry_point: "continue where I left off",
    recommended_minutes: 15,
    recommended_guide_mode: "coach",
    recommendation: baseRecommendation,
    timing_decision: "later_today",
    timing_reason: "The next preferred study window begins later today.",
    scheduled_for: "2026-04-06T07:30:00-04:00",
    local_timezone: "America/New_York",
  };

  const scheduledPlan = {
    user_id: "demo-user",
    delivery_status: "scheduled",
    delivery_channel: "push",
    deliver_at: "2026-04-06T07:30:00-04:00",
    fallback_at: "2026-04-06T07:30:00-04:00",
    idempotency_key: "demo-user:theme:continue where I left off:2026-04-06T07:30:00-04:00",
    reason: "This push can be queued for the user's next preferred study window so the user can build on a completed step.",
    nudge: scheduledNudge,
  };

  if (scenario === "first_visit") {
    return {
      profile: firstVisitProfile,
      recommendation: {
        ...baseRecommendation,
        focus_area: "consistency",
        recommended_guide_mode: "guide",
        recommended_minutes: 10,
        recommended_entry_point: "I want to begin gently",
        reason: "Emmaus is starting with a short, welcoming session that feels safe on mobile and easy to finish in one sitting.",
        suggested_action: "Finish one short session, then carry one sentence of prayer with you into the next part of the day.",
      },
      streaks: { user_id: "demo-user", completed_sessions: 0, current_streak: 0, longest_streak: 0, last_completed_on: null },
      actionItems: [],
      latestMood: null,
      activeSession: null,
      memorySummary: firstVisitMemorySummary,
      nudge: {
        ...scheduledNudge,
        nudge_type: "encouragement",
        title: "A gentle first step",
        message: "Start with one short session, answer honestly, and let Emmaus begin learning where you need clarity and follow-through.",
        timing_decision: "now",
        timing_reason: "No preferred study window is configured yet, so Emmaus can prompt gently right away.",
        scheduled_for: null,
      },
      nudgePlan: {
        ...scheduledPlan,
        delivery_status: "send_now",
        deliver_at: "2026-04-05T09:00:00-04:00",
        fallback_at: "2026-04-05T09:00:00-04:00",
        idempotency_key: "demo-user:encouragement:I want to begin gently:2026-04-05T09:00:00-04:00",
        reason: "A first-time user can be nudged immediately while setting a rhythm.",
      },
    };
  }

  if (scenario === "comprehension_gap") {
    return {
      profile: { ...baseProfile, current_streak: 1, longest_streak: 6, last_completed_on: "2026-04-03" },
      recommendation: {
        user_id: "demo-user",
        focus_area: "comprehension",
        recommended_reference: { book: "Mark", chapter: 4, start_verse: 35, end_verse: 41 },
        recommended_guide_mode: "guide",
        recommended_minutes: 12,
        recommended_entry_point: "I need clarity before application",
        reason: "Recent responses moved quickly to personal reaction, so Emmaus is slowing this session down and revisiting what the passage actually says.",
        suggested_action: "Write one sentence about what this passage reveals about Christ before deciding what to do next.",
        gap_report: {
          user_id: "demo-user",
          comprehension_gap: 0.82,
          application_gap: 0.34,
          consistency_gap: 0.29,
          focus_area: "comprehension",
          observed_patterns: [
            "Recent answers jumped to feelings before identifying what the text says.",
            "Interpretation questions have needed more second-pass clarity than application questions.",
          ],
        },
      },
      streaks: { user_id: "demo-user", completed_sessions: 4, current_streak: 1, longest_streak: 6, last_completed_on: "2026-04-03" },
      actionItems: [completedActionHistory[1]],
      latestMood: { user_id: "demo-user", mood: "neutral", energy: "medium", notes: "I feel willing to study, but I keep realizing I move too fast through the meaning.", created_at: "2026-04-05T06:50:00-04:00" },
      activeSession: null,
      memorySummary: {
        ...baseMemorySummary,
        latest_summary: "Emmaus noticed the user keeps reacting quickly, so the next step is to slow down and let Christ's words set the pace.",
        recurring_themes: ["slowing down in Scripture", "Christ calming fear"],
        growth_areas: ["reading for meaning before reaction", "naming what the text says about Jesus"],
        carry_forward_prompt: "Return to Christ's calming presence and name what the passage says before you decide what to do with it.",
        recent_references: ["Mark 4:35-41", "Luke 24:13-17"],
      },
      nudge: {
        user_id: "demo-user",
        nudge_type: "encouragement",
        title: "Slow down and read for clarity",
        message: "Emmaus is recommending a shorter session that stays close to the text before moving into application.",
        recommended_entry_point: "I need clarity before application",
        recommended_minutes: 12,
        recommended_guide_mode: "guide",
        recommendation: {
          user_id: "demo-user",
          focus_area: "comprehension",
          recommended_reference: { book: "Mark", chapter: 4, start_verse: 35, end_verse: 41 },
          recommended_guide_mode: "guide",
          recommended_minutes: 12,
          recommended_entry_point: "I need clarity before application",
          reason: "Recent responses moved quickly to personal reaction, so Emmaus is slowing this session down and revisiting what the passage actually says.",
          suggested_action: "Write one sentence about what this passage reveals about Christ before deciding what to do next.",
          gap_report: {
            user_id: "demo-user",
            comprehension_gap: 0.82,
            application_gap: 0.34,
            consistency_gap: 0.29,
            focus_area: "comprehension",
            observed_patterns: [
              "Recent answers jumped to feelings before identifying what the text says.",
              "Interpretation questions have needed more second-pass clarity than application questions.",
            ],
          },
        },
        timing_decision: "now",
        timing_reason: "The user is inside the preferred study window and this is a good moment for a short reset session.",
        scheduled_for: null,
        local_timezone: "America/New_York",
      },
      nudgePlan: {
        user_id: "demo-user",
        delivery_status: "send_now",
        delivery_channel: "push",
        deliver_at: "2026-04-05T07:05:00-04:00",
        fallback_at: "2026-04-05T07:05:00-04:00",
        idempotency_key: "demo-user:encouragement:I need clarity before application:2026-04-05T07:05:00-04:00",
        reason: "Emmaus can send this reset-style nudge now because the user is available and the recommended session is short.",
        nudge: {
          user_id: "demo-user",
          nudge_type: "encouragement",
          title: "Slow down and read for clarity",
          message: "Emmaus is recommending a shorter session that stays close to the text before moving into application.",
          recommended_entry_point: "I need clarity before application",
          recommended_minutes: 12,
          recommended_guide_mode: "guide",
          recommendation: {
            user_id: "demo-user",
            focus_area: "comprehension",
            recommended_reference: { book: "Mark", chapter: 4, start_verse: 35, end_verse: 41 },
            recommended_guide_mode: "guide",
            recommended_minutes: 12,
            recommended_entry_point: "I need clarity before application",
            reason: "Recent responses moved quickly to personal reaction, so Emmaus is slowing this session down and revisiting what the passage actually says.",
            suggested_action: "Write one sentence about what this passage reveals about Christ before deciding what to do next.",
            gap_report: {
              user_id: "demo-user",
              comprehension_gap: 0.82,
              application_gap: 0.34,
              consistency_gap: 0.29,
              focus_area: "comprehension",
              observed_patterns: [
                "Recent answers jumped to feelings before identifying what the text says.",
                "Interpretation questions have needed more second-pass clarity than application questions.",
              ],
            },
          },
          timing_decision: "now",
          timing_reason: "The user is inside the preferred study window and this is a good moment for a short reset session.",
          scheduled_for: null,
          local_timezone: "America/New_York",
        },
      },
    };
  }

  if (scenario === "in_progress") {
    return {
      profile: baseProfile,
      recommendation: baseRecommendation,
      streaks: { user_id: "demo-user", completed_sessions: 6, current_streak: 3, longest_streak: 6, last_completed_on: "2026-04-04" },
      actionItems: completedActionHistory,
      latestMood: { user_id: "demo-user", mood: "peaceful", energy: "medium", notes: "Ready for a focused morning session, but I want the application to land somewhere concrete.", created_at: "2026-04-05T07:25:00-04:00" },
      activeSession,
      memorySummary: baseMemorySummary,
      nudge: scheduledNudge,
      nudgePlan: scheduledPlan,
    };
  }

  if (scenario === "overdue_action") {
    return {
      profile: { ...baseProfile, current_streak: 0, last_completed_on: "2026-04-02" },
      recommendation: baseRecommendation,
      streaks: { user_id: "demo-user", completed_sessions: 6, current_streak: 0, longest_streak: 6, last_completed_on: "2026-04-02" },
      actionItems: overdueActionItems,
      latestMood: { user_id: "demo-user", mood: "neutral", energy: "medium", notes: "Need a simple next step to restart.", created_at: "2026-04-05T08:00:00-04:00" },
      activeSession: null,
      memorySummary: {
        ...baseMemorySummary,
        latest_summary: "Emmaus is carrying forward a recent encouragement step that still needs follow-through.",
        growth_areas: ["closing the loop on next steps", "restarting gently after missing a few days"],
        carry_forward_prompt: "Follow through on the encouragement Emmaus already surfaced before you begin something new.",
      },
      nudge: {
        ...scheduledNudge,
        nudge_type: "follow_through",
        title: "Follow through on your last step",
        message: "Before starting something new, finish what your last session already surfaced.",
        timing_decision: "now",
        timing_reason: "You are in a good study window, and one unfinished next step is still waiting.",
        scheduled_for: null,
      },
      nudgePlan: {
        ...scheduledPlan,
        delivery_status: "send_now",
        deliver_at: "2026-04-05T12:30:00-04:00",
        fallback_at: "2026-04-05T12:30:00-04:00",
        idempotency_key: "demo-user:follow_through:continue where I left off:2026-04-05T12:30:00-04:00",
        reason: "A follow-through reminder can go out now because this next step is overdue and the user is available.",
      },
    };
  }

  if (scenario === "scheduled_nudge") {
    return {
      profile: { ...baseProfile, current_streak: 4, longest_streak: 8 },
      recommendation: { ...baseRecommendation, focus_area: "growth", recommended_guide_mode: "challenger", reason: "The user has momentum, so Emmaus can stretch the next session a bit more." },
      streaks: { user_id: "demo-user", completed_sessions: 9, current_streak: 4, longest_streak: 8, last_completed_on: "2026-04-05" },
      actionItems: scheduledActionHistory,
      latestMood: { user_id: "demo-user", mood: "encouraged", energy: "high", notes: "Open to a deeper challenge tomorrow morning and grateful for the last few concrete wins.", created_at: "2026-04-05T20:45:00-04:00" },
      activeSession: null,
      memorySummary: {
        ...baseMemorySummary,
        latest_summary: "Emmaus has seen healthier momentum and is now inviting the user to go deeper instead of only staying practical.",
        recurring_themes: ["Christ's faithfulness", "deeper reflection with follow-through"],
        growth_areas: ["embracing a harder challenge without losing specificity"],
        carry_forward_prompt: "Return to Christ's faithfulness and let the next session challenge one comfortable assumption.",
      },
      nudge: scheduledNudge,
      nudgePlan: scheduledPlan,
    };
  }

  return {
    profile: baseProfile,
    recommendation: baseRecommendation,
    streaks: { user_id: "demo-user", completed_sessions: 6, current_streak: 3, longest_streak: 6, last_completed_on: "2026-04-04" },
    actionItems: [completedActionHistory[0]],
    latestMood: { user_id: "demo-user", mood: "peaceful", energy: "medium", notes: "Ready for today's plan and encouraged by one recent follow-through win.", created_at: "2026-04-05T07:25:00-04:00" },
    activeSession: null,
    memorySummary: baseMemorySummary,
    nudge: {
      ...scheduledNudge,
      timing_decision: "now",
      timing_reason: "The user is already inside the preferred study window.",
      scheduled_for: null,
    },
    nudgePlan: {
      ...scheduledPlan,
      delivery_status: "send_now",
      deliver_at: "2026-04-05T07:32:00-04:00",
      fallback_at: "2026-04-05T07:32:00-04:00",
      idempotency_key: "demo-user:momentum:continue where I left off:2026-04-05T07:32:00-04:00",
      reason: "Emmaus can send this reminder now because the user is already in the preferred window.",
    },
  };
}
function renderTextSourceOptions() {
  const sources = state.textSources.length ? state.textSources : DEFAULT_TEXT_SOURCES;
  const options = sources
    .map((source) => `<option value="${escapeHtml(source.source_id)}">${escapeHtml(source.name)}</option>`)
    .join("");

  if (elements.textSourceSelect) {
    elements.textSourceSelect.innerHTML = options;
  }
  if (elements.preferredSourceSelect) {
    elements.preferredSourceSelect.innerHTML = options;
  }

  const preferredSourceId = getEffectivePreferredSourceId(sources);
  const activeSessionSourceId = state.activeSessionPayload?.session?.text_source_id || "";
  const sessionSourceId = activeSessionSourceId || preferredSourceId;

  if (preferredSourceId && elements.preferredSourceSelect) {
    elements.preferredSourceSelect.value = preferredSourceId;
  }
  if (sessionSourceId && elements.textSourceSelect) {
    elements.textSourceSelect.value = sessionSourceId;
  }

  renderBibleSourceManager();
}

async function loadLiveDashboard({ restoreScreen = false } = {}) {
  const userId = getUserId();
  state.userId = userId;
  localStorage.setItem("emmaus.userId", userId);

  const [profile, recommendation, streaks, actionItemsResponse, prayerItemsResponse, reviewHistory, latestMood, activeSession, memorySummary, lookBack] = await Promise.all([
    fetchJson(`/v1/users/${encodeURIComponent(userId)}/profile`),
    fetchJson(`/v1/agent/recommendations/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/engagement/streaks/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/action-items/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/prayer-items/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/review/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/mood/${encodeURIComponent(userId)}`, { allowNull: true }),
    fetchJson(`/v1/agent/session/active/${encodeURIComponent(userId)}`, { allowNull: true }),
    fetchJson(`/v1/users/${encodeURIComponent(userId)}/memory`, { allowNull: true }),
    fetchJson(`/v1/study/look-back/${encodeURIComponent(userId)}`, { allowNull: true }),
  ]);

  state.profile = profile;
  state.recommendation = recommendation;
  state.streaks = streaks;
  state.actionItems = actionItemsResponse.items || [];
  state.prayerItems = prayerItemsResponse.items || [];
  state.reviewHistory = reviewHistory;
  state.latestMood = latestMood;
  state.activeSessionPayload = activeSession;
  state.currentQuestion = activeSession?.current_question || null;
  state.memorySummary = memorySummary;
  state.lookBack = lookBack;
  state.nudge = null;
  state.nudgePlan = null;

  renderDashboardShell({
    profile,
    recommendation,
    streaks,
    actionItems: state.actionItems,
    prayerItems: state.prayerItems,
    latestMood,
    activeSession,
  });

  try {
    await loadNudgeArtifacts();
  } catch (error) {
    handleError(error);
  }
  renderTodayPlan(recommendation, activeSession, state.actionItems, state.memorySummary);
  if (restoreScreen) {
    restorePreferredScreen();
  }
}

function renderDemoDashboard({ restoreScreen = false } = {}) {
  const demo = buildDemoScenarioData(state.demoScenario);
  state.userId = demo.profile.user_id;
  state.profile = demo.profile;
  state.recommendation = demo.recommendation;
  state.streaks = demo.streaks;
  state.actionItems = demo.actionItems;
  state.prayerItems = demo.prayerItems || [];
  state.reviewHistory = demo.reviewHistory || null;
  state.latestMood = demo.latestMood;
  state.activeSessionPayload = demo.activeSession;
  state.currentQuestion = demo.activeSession?.current_question || null;
  state.nudge = demo.nudge;
  state.nudgePlan = demo.nudgePlan;
  state.memorySummary = demo.memorySummary;
  state.lookBack = demo.lookBack || null;

  renderDashboardShell({
    profile: demo.profile,
    recommendation: demo.recommendation,
    streaks: demo.streaks,
    actionItems: demo.actionItems,
    prayerItems: demo.prayerItems || [],
    latestMood: demo.latestMood,
    activeSession: demo.activeSession,
  });
  renderNudge(demo.nudge, demo.nudgePlan);
  renderTodayPlan(demo.recommendation, demo.activeSession, demo.actionItems, demo.memorySummary);
  if (restoreScreen) {
    restorePreferredScreen();
  }
}

function renderDashboardShell({ profile, recommendation, streaks, actionItems, prayerItems, latestMood, activeSession }) {
  renderHero(profile, recommendation, activeSession, actionItems);
  renderProfile(profile);
  renderRecommendation(recommendation, state.memorySummary);
  renderLookBack(state.lookBack);
  renderMemorySummary(state.memorySummary);
  renderStreaks(streaks);
  renderActionItems(actionItems);
  renderPrayerItems(prayerItems || []);
  renderReviewHistory(state.reviewHistory);
  renderCompletionSummary(state.memorySummary, actionItems);
  renderLatestMood(latestMood);
  renderOnboarding(profile, streaks, activeSession, actionItems);
  updateSessionEntryState(activeSession);
  renderDemoControls();

  if (activeSession) {
    renderSessionStart(activeSession, { navigate: false });
    localStorage.setItem("emmaus.activeSessionId", activeSession.session.session_id);
  } else {
    clearSessionView();
    localStorage.removeItem("emmaus.activeSessionId");
  }
}

function renderLookBack(lookBack) {
  if (!elements.lookBackCard || !elements.lookBackPill || !elements.lookBackForm || !elements.lookBackResponseText) {
    return;
  }

  const prompt = lookBack?.prompt || null;
  const latestReview = lookBack?.latest_review || null;
  const recentReviews = safeArray(lookBack?.recent_reviews).slice(0, 3);
  const historyMarkup = recentReviews.length
    ? `
      <div class="review-response-list look-back-history-list">
        ${recentReviews.map((review) => `
          <div class="inline-card review-response-card look-back-history-card">
            <p><strong>${escapeHtml(formatReference(review.reference))}</strong></p>
            <p class="micro-copy">${escapeHtml(buildLookBackOutcomeLabel(review.outcome))}</p>
            <p>${escapeHtml(truncateGuideCopy(review.encouragement, 120))}</p>
          </div>
        `).join("")}
      </div>
    `
    : "";

  const lookBackPanelEl = elements.lookBackCard.closest(".panel");
  if (prompt) {
    if (lookBackPanelEl) lookBackPanelEl.classList.remove("hidden");
    elements.lookBackPill.textContent = "Ready";
    elements.lookBackCard.innerHTML = `
      <div class="memory-card">
        <p><strong>${escapeHtml(formatReference(prompt.reference))}</strong></p>
        <p>${escapeHtml(prompt.prompt)}</p>
        <p class="micro-copy">${escapeHtml(prompt.support_text)}</p>
        ${historyMarkup ? `<p class="micro-copy"><strong>Recent reinforcement</strong></p>${historyMarkup}` : ""}
      </div>
    `;
    elements.lookBackForm.classList.remove("hidden");
    return;
  }

  elements.lookBackResponseText.value = "";
  elements.lookBackForm.classList.add("hidden");

  if (latestReview) {
    if (lookBackPanelEl) lookBackPanelEl.classList.remove("hidden");
    elements.lookBackPill.textContent = "Saved";
    elements.lookBackCard.innerHTML = `
      <div class="memory-card">
        <p><strong>${escapeHtml(formatReference(latestReview.reference))}</strong></p>
        <p class="today-plan-copy">${escapeHtml(latestReview.encouragement)}</p>
        <div class="inline-card">
          <p><strong>You remembered</strong></p>
          <p>${escapeHtml(latestReview.response_text)}</p>
        </div>
        ${historyMarkup ? `<p class="micro-copy"><strong>Recent reinforcement</strong></p>${historyMarkup}` : ""}
      </div>
    `;
    return;
  }

  elements.lookBackPill.textContent = "Ready";
  elements.lookBackCard.innerHTML = '<p class="empty-state">Finish a session and Emmaus will bring one recent truth back into view here.</p>';
  const lookBackPanel = elements.lookBackCard.closest(".panel");
  if (lookBackPanel) lookBackPanel.classList.add("hidden");
}

function buildLookBackOutcomeLabel(outcome) {
  if (outcome === "clear") {
    return "Stayed with you clearly";
  }
  if (outcome === "partial") {
    return "Partly stayed with you";
  }
  return "Still needs reinforcement";
}

function renderHero(profile, recommendation, activeSession, actionItems) {
  if (activeSession) {
    elements.heroTitle.textContent = "Return to the question Christ placed in front of you.";
    elements.heroCopy.textContent = `Resume ${formatReference(activeSession.session.reference)} and keep moving from reflection toward obedience.`;
    elements.heroPrimaryButton.textContent = "Resume Session";
    return;
  }

  const openAction = actionItems.find((item) => item.status === "open");
  if (openAction) {
    elements.heroTitle.textContent = "Carry what you studied into your day.";
    elements.heroCopy.textContent = "Emmaus is surfacing your unfinished next step first so reflection becomes real follow-through.";
    elements.heroPrimaryButton.textContent = "Review Next Step";
    return;
  }

  if (profile?.completed_sessions === 0) {
    elements.heroTitle.textContent = "Begin a Christ-centered study rhythm that can grow with you.";
    elements.heroCopy.textContent = "Emmaus starts simple on mobile, then adapts to your schedule, habits, and areas that still need clarity or application.";
    elements.heroPrimaryButton.textContent = "Start Today's Plan";
    return;
  }

  elements.heroTitle.textContent = "Your guide for Scripture, reflection, and response.";
  elements.heroCopy.textContent = recommendation
    ? `Emmaus is shaping today's session around ${humanizeFocusArea(recommendation.focus_area).toLowerCase()} so the next step fits your real needs, not a generic plan.`
    : "Emmaus adapts each session to your habits, understanding, and next step of obedience.";
  elements.heroPrimaryButton.textContent = "Start Today's Plan";
}

function getTranslationTemplates() {
  return state.translationTemplates.length ? state.translationTemplates : DEFAULT_TRANSLATION_TEMPLATES;
}

function renderTranslationTemplates(sources, preferredSourceId) {
  const sourceUi = bibleSourceElements();
  if (!sourceUi.templateList) {
    return;
  }

  const templates = getTranslationTemplates();
  sourceUi.templateList.innerHTML = `
    <div class="translation-template-grid">
      ${templates.map((template) => buildTranslationTemplateCard(template, sources, preferredSourceId)).join("")}
    </div>
  `;
}

function buildTranslationTemplateCard(template, sources, preferredSourceId) {
  const connectedSource = template.source_id ? sources.find((source) => source.source_id === template.source_id) : null;
  const isCurrent = Boolean(connectedSource && preferredSourceId === connectedSource.source_id);
  let actionLabel = "Choose";
  if (template.setup_mode === "starter") {
    actionLabel = isCurrent ? "Using now" : "Use included Bible";
  } else if (template.setup_mode === "esv_api") {
    actionLabel = connectedSource ? (isCurrent ? "Using ESV" : "Use connected ESV") : "Connect ESV";
  } else if (template.setup_mode === "upload") {
    actionLabel = `Set up ${template.name}`;
  } else {
    actionLabel = `Connect ${template.name}`;
  }

  const meta = [];
  if (template.recommended) {
    meta.push('<span class="meta-pill">Recommended</span>');
  }
  if (isCurrent) {
    meta.push('<span class="meta-pill">Current</span>');
  } else if (connectedSource) {
    meta.push('<span class="meta-pill">Connected</span>');
  }
  meta.push(`<span class="meta-pill">${escapeHtml(sentenceCase(template.setup_mode.replaceAll("_", " ")))}</span>`);

  const previewButton = connectedSource || template.setup_mode === "starter"
    ? `<button class="action-button" type="button" data-template-preview-source="${escapeHtml((connectedSource?.source_id || template.source_id || STARTER_SOURCE_ID))}">Preview sample</button>`
    : "";
  const actionClass = previewButton ? "source-card-actions dual-actions" : "source-card-actions";

  return `
    <article class="action-card translation-template-card ${isCurrent ? "selected" : ""}">
      <div>
        <p><strong>${escapeHtml(template.name)}</strong></p>
        <p>${escapeHtml(template.description)}</p>
      </div>
      <div class="template-meta">${meta.join("")}</div>
      <div class="${actionClass}">
        <button class="action-button" type="button" data-template-action="${escapeHtml(template.setup_mode)}" data-template-name="${escapeHtml(template.name)}" ${isCurrent ? "disabled" : ""}>${escapeHtml(actionLabel)}</button>
        ${previewButton}
      </div>
    </article>
  `;
}

function setBibleManagerExpanded(expanded) {
  state.bibleManagerExpanded = expanded;
  const sourceUi = bibleSourceElements();
  sourceUi.details?.classList.toggle("hidden", !expanded);
  if (!expanded) {
    setBibleSetupExpanded(false);
  }
  if (sourceUi.manageToggle) {
    sourceUi.manageToggle.textContent = expanded ? "Hide Bible options" : "Manage Bible";
    sourceUi.manageToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
  }
}

function setBibleSetupExpanded(expanded) {
  state.bibleSetupExpanded = expanded;
  const sourceUi = bibleSourceElements();
  sourceUi.setupOptions?.classList.toggle("hidden", !expanded);
  if (sourceUi.advancedToggle) {
    sourceUi.advancedToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    sourceUi.advancedToggle.textContent = expanded ? "Hide setup options" : "More setup options";
  }
}

function onToggleBibleManager() {
  setBibleManagerExpanded(!state.bibleManagerExpanded);
}

function renderSourcePreview(preview) {
  if (!elements.sourcePreviewCard) {
    return;
  }
  if (!preview) {
    elements.sourcePreviewCard.innerHTML = '<div class="action-card source-preview-card"><p><strong>Preview a sample passage</strong></p><p class="micro-copy">Tap Preview sample on a connected Bible to compare how it reads before choosing it.</p></div>';
    return;
  }

  elements.sourcePreviewCard.innerHTML = `
    <div class="action-card source-preview-card">
      <p class="panel-label">Sample preview</p>
      <p><strong>${escapeHtml(preview.translation_name)}</strong> - ${escapeHtml(formatReference(preview.reference))}</p>
      <p>${escapeHtml(preview.text)}</p>
      ${preview.copyright_notice ? `<p class="micro-copy">${escapeHtml(preview.copyright_notice)}</p>` : ""}
    </div>
  `;
}

async function previewBibleSource(sourceId) {
  if (!sourceId) {
    return;
  }

  try {
    if (isDemoMode()) {
      const demoPassage = state.activeSessionPayload?.passage || {
        source_id: STARTER_SOURCE_ID,
        translation_name: "Included Starter Bible",
        reference: { book: "John", chapter: 3, start_verse: 16, end_verse: 17 },
        text: "For God so loved the world, that he gave his only begotten Son, that whoever believes in him should not perish, but have everlasting life.",
        copyright_notice: "Public Domain",
      };
      state.sourcePreview = { ...demoPassage, source_id: sourceId };
      renderSourcePreview(state.sourcePreview);
    } else {
      const preview = await fetchJson("/v1/texts/passage", {
        method: "POST",
        body: {
          source_id: sourceId,
          book: "John",
          chapter: 3,
          start_verse: 16,
          end_verse: 17,
        },
      });
      state.sourcePreview = preview;
      renderSourcePreview(preview);
    }

    if (elements.sourcePreviewCard) {
      elements.sourcePreviewCard.classList.remove("preview-card-active");
      void elements.sourcePreviewCard.offsetWidth;
      elements.sourcePreviewCard.classList.add("preview-card-active");
      elements.sourcePreviewCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      window.setTimeout(() => {
        elements.sourcePreviewCard?.classList.remove("preview-card-active");
      }, 1400);
    }

    const previewName = getSourceById(sourceId)?.name || state.sourcePreview?.translation_name || "this Bible";
    showToast(`Showing a sample from ${previewName}.`);
  } catch (error) {
    handleError(error);
  }
}

function renderProfile(profile) {
  const preferences = profile?.preferences || {};
  elements.userIdInput.value = profile?.user_id || state.userId;
  elements.displayNameInput.value = profile?.display_name || "";
  elements.preferredMinutesInput.value = preferences.preferred_session_minutes || "";
  elements.guideModeSelect.value = preferences.preferred_guide_mode || "guide";
  elements.questionStyleSelect.value = preferences.preferred_question_style || "reflective";
  elements.guidanceToneSelect.value = preferences.preferred_guidance_tone || "steady";
  elements.nudgeIntensitySelect.value = preferences.nudge_intensity || "balanced";
  elements.timezoneInput.value = preferences.timezone || "America/New_York";
  elements.studyWindowStartInput.value = preferences.preferred_study_window_start || "";
  elements.studyWindowEndInput.value = preferences.preferred_study_window_end || "";
  elements.quietHoursStartInput.value = preferences.quiet_hours_start || "";
  elements.quietHoursEndInput.value = preferences.quiet_hours_end || "";
  state.selectedStudyDays = Array.isArray(preferences.preferred_study_days) ? [...preferences.preferred_study_days] : [];
  updateStudyDayChips();
  renderTextSourceOptions();

  if (preferences.preferred_translation_source_id) {
    elements.preferredSourceSelect.value = preferences.preferred_translation_source_id;
    if (!state.activeSessionPayload) {
      elements.textSourceSelect.value = preferences.preferred_translation_source_id;
    }
  }
}

function renderRecommendation(recommendation, memorySummary) {
    if (!recommendation) {
      elements.focusPill.textContent = "Waiting";
      elements.recommendationCard.innerHTML = '<p class="empty-state">No recommendation is available yet.</p>';
      return;
    }

    const reasonSummary = buildTodayReasonSummary(recommendation);
    const carryForwardCopy = buildTodayCarryForwardCopy(memorySummary);
    const emphasisPattern = truncateGuideCopy(polishGuideCopy(safeArray(recommendation.gap_report?.observed_patterns)[0] || ""), 110);
    const supportCopy = carryForwardCopy || emphasisPattern;
    const supportLabel = carryForwardCopy ? "Building on:" : "Pay attention to:";
    const suggestedAction = truncateGuideCopy(polishGuideCopy(recommendation.suggested_action), 115);

    elements.focusPill.textContent = humanizeFocusArea(recommendation.focus_area);
    elements.recommendationCard.innerHTML = `
      <div class="recommendation-card compact-recommendation-card">
        <p><strong>${escapeHtml(formatReference(recommendation.recommended_reference))}</strong></p>
        <p class="today-plan-copy">${escapeHtml(reasonSummary)}</p>
        <div class="recommendation-meta">
          <span class="meta-pill">${escapeHtml(humanizeGuideMode(recommendation.recommended_guide_mode))}</span>
          <span class="meta-pill">${escapeHtml(String(recommendation.recommended_minutes))} min</span>
        </div>
        ${supportCopy ? `<p class="recommendation-support"><strong>${escapeHtml(supportLabel)}</strong> ${escapeHtml(supportCopy)}</p>` : ""}
        <p class="memory-prompt"><strong>Next step:</strong> ${escapeHtml(suggestedAction)}</p>
      </div>
    `;
  }

function renderMemorySummary(memorySummary) {
  if (!memorySummary || !memorySummary.memory_count) {
    elements.memoryThreadPill.textContent = "Ready";
    elements.memoryThreadCard.innerHTML = `
      <div class="memory-card">
        <p><strong>Emmaus will start noticing your growth here.</strong></p>
        <p class="today-plan-copy">Complete a few sessions and this card will show the themes Christ keeps bringing back into view.</p>
      </div>
    `;
    return;
  }

  elements.memoryThreadPill.textContent = `${memorySummary.memory_count} ${memorySummary.memory_count === 1 ? "thread" : "threads"}`;
  const latestSummary = truncateGuideCopy(polishGuideCopy(memorySummary.latest_summary || "Emmaus is carrying a recent thread forward."), 145);
  const carryForwardPrompt = truncateGuideCopy(polishGuideCopy(memorySummary.carry_forward_prompt || ""), 120);
  const primaryTheme = safeArray(memorySummary.recurring_themes)[0] || null;
  const secondaryTheme = safeArray(memorySummary.recurring_themes)[1] || null;
  const mainGrowthArea = safeArray(memorySummary.growth_areas)[0] || null;
  const latestReference = safeArray(memorySummary.recent_references)[0] || null;
  const themeChips = [primaryTheme, secondaryTheme]
    .filter(Boolean)
    .map((theme) => `<span class="meta-pill">${escapeHtml(theme)}</span>`)
    .join("");

  elements.memoryThreadCard.innerHTML = `
    <div class="memory-card compact-memory-card">
      <p><strong>${escapeHtml(latestSummary)}</strong></p>
      ${themeChips ? `<div class="memory-theme-list">${themeChips}</div>` : ""}
      ${mainGrowthArea ? `<p class="today-plan-copy"><strong>Growth edge:</strong> ${escapeHtml(mainGrowthArea)}</p>` : ""}
      ${carryForwardPrompt ? `<p class="memory-prompt"><strong>Keep building here:</strong> ${escapeHtml(carryForwardPrompt)}</p>` : ""}
      ${latestReference ? `<p class="micro-copy">Recent thread: ${escapeHtml(latestReference)}</p>` : ""}
    </div>
  `;
}

function renderStreaks(streaks) {
  const currentStreak = streaks?.current_streak || 0;
  const completedSessions = streaks?.completed_sessions || 0;
  elements.streakValue.textContent = `${currentStreak} ${currentStreak === 1 ? "day" : "days"} of rhythm`;

  if (!completedSessions) {
    elements.streakCopy.textContent = "Complete your first session and Emmaus will begin learning your rhythm.";
    return;
  }

  const lastCompleted = streaks.last_completed_on ? ` Last completed ${formatDateOnly(streaks.last_completed_on)}.` : "";
  elements.streakCopy.textContent = `Completed sessions: ${completedSessions}. Longest streak: ${streaks.longest_streak}.${lastCompleted}`;
}

function renderLatestMood(latestMood) {
  if (!latestMood) {
    elements.latestMoodCopy.textContent = "No mood check-in saved yet.";
    return;
  }

  const notes = latestMood.notes ? ` ${latestMood.notes}` : "";
  elements.latestMoodCopy.textContent = `${sentenceCase(latestMood.mood)}, ${latestMood.energy} energy.${notes}`;
  if (latestMood.mood) {
    selectMood(latestMood.mood);
  }
  if (latestMood.energy) {
    elements.energySelect.value = latestMood.energy;
  }
  elements.moodNotes.value = latestMood.notes || "";
}

function renderOnboarding(profile, streaks, activeSession, actionItems) {
  const openActions = actionItems.filter((item) => item.status === "open");
  const shouldShow = shouldShowOnboarding(profile, streaks, activeSession, openActions);

  if (!shouldShow) {
    elements.onboardingPanel.classList.add("hidden");
    return;
  }

  const step = deriveOnboardingStep(profile);
  state.onboardingStep = step;
  elements.onboardingPanel.classList.remove("hidden");
  elements.onboardingStepPill.textContent = `Step ${step} of 4`;

  if (step === 1) {
    elements.onboardingCopy.textContent = "Start by choosing a Bible. Emmaus includes one right away, so you can begin in one tap.";
    elements.onboardingFlow.innerHTML = `
      <div class="today-plan-card onboarding-step-card">
        <p><strong>Choose your Bible</strong></p>
        <p class="today-plan-copy">Most people should start with the included Bible and begin studying right away.</p>
        <div class="source-quick-actions">
          <button class="primary-button full-width" type="button" data-action="onboarding-use-starter">Use included starter Bible</button>
          <button class="secondary-button full-width" type="button" data-action="onboarding-use-esv">${getSourceById(ESV_SOURCE_ID) ? "Use connected ESV" : "Connect ESV with API key"}</button>
          <button class="secondary-button full-width" type="button" data-action="onboarding-focus-upload">Upload Bible from this device</button>
          <button class="secondary-button full-width" type="button" data-action="onboarding-focus-advanced">Use a licensed provider</button>
        </div>
      </div>
    `;
    return;
  }

  if (step === 2) {
    elements.onboardingCopy.textContent = "Pick a session length that feels realistic on your phone, even on a busy day.";
    elements.onboardingFlow.innerHTML = `
      <div class="today-plan-card onboarding-step-card">
        <p><strong>How much time feels realistic?</strong></p>
        <div class="chip-row onboarding-choice-row">
          <button class="choice-chip" type="button" data-action="onboarding-set-minutes" data-minutes="10">10 min</button>
          <button class="choice-chip" type="button" data-action="onboarding-set-minutes" data-minutes="15">15 min</button>
          <button class="choice-chip" type="button" data-action="onboarding-set-minutes" data-minutes="20">20 min</button>
        </div>
        <p class="micro-copy">Emmaus will use this to shape your first sessions and future nudges.</p>
      </div>
    `;
    return;
  }

  if (step === 3) {
    elements.onboardingCopy.textContent = "Tell Emmaus the best time of day to reach you so today's plan and future reminders fit your rhythm.";
    elements.onboardingFlow.innerHTML = `
      <div class="today-plan-card onboarding-step-card">
        <p><strong>When do you usually study best?</strong></p>
        <div class="chip-row onboarding-choice-row">
          <button class="choice-chip" type="button" data-action="onboarding-set-window" data-window="morning">Morning</button>
          <button class="choice-chip" type="button" data-action="onboarding-set-window" data-window="midday">Midday</button>
          <button class="choice-chip" type="button" data-action="onboarding-set-window" data-window="evening">Evening</button>
        </div>
        <p class="micro-copy">You can fine-tune quiet hours and study days later in your preferences.</p>
      </div>
    `;
    return;
  }

  elements.onboardingCopy.textContent = "Your starter rhythm is ready. Emmaus can launch today's first guided session now.";
  const recommendation = state.recommendation;
  elements.onboardingFlow.innerHTML = `
    <div class="today-plan-card onboarding-step-card">
      <p><strong>Start your first session</strong></p>
      <p class="today-plan-copy">${escapeHtml(recommendation ? recommendation.reason : "Emmaus is ready with a first guided session.")}</p>
      <div class="today-plan-actions">
        <span class="meta-pill">${escapeHtml(String(recommendation?.recommended_minutes || state.profile?.preferences?.preferred_session_minutes || 15))} min</span>
        <span class="meta-pill">${escapeHtml(humanizeGuideMode(recommendation?.recommended_guide_mode || "guide"))}</span>
      </div>
      <div class="source-quick-actions">
        <button class="primary-button full-width" type="button" data-action="onboarding-start-session">Start today's first session</button>
        <button class="secondary-button full-width" type="button" data-action="focus-identity">Adjust more preferences first</button>
      </div>
    </div>
  `;
}

function shouldShowOnboarding(profile, streaks, activeSession, openActions) {
  if (isDemoMode()) {
    return false;
  }
  if (activeSession || openActions.length) {
    return false;
  }
  if (streaks?.completed_sessions > 0 || isOnboardingComplete()) {
    return false;
  }
  return true;
}

function deriveOnboardingStep(profile) {
  const preferences = profile?.preferences || {};
  const storedStep = getStoredOnboardingStep();
  if (!preferences.preferred_translation_source_id) {
    return 1;
  }
  if (storedStep <= 1) {
    return 2;
  }
  if (!preferences.preferred_study_window_start || !preferences.preferred_study_window_end) {
    return Math.max(3, storedStep || 3);
  }
  return Math.max(4, storedStep || 4);
}

function onboardingStorageKey(name) {
  return `emmaus.onboarding.${getUserId()}.${name}`;
}

function getStoredOnboardingStep() {
  return Number(localStorage.getItem(onboardingStorageKey("step")) || "1");
}

function setStoredOnboardingStep(step) {
  state.onboardingStep = step;
  localStorage.setItem(onboardingStorageKey("step"), String(step));
}

function isOnboardingComplete() {
  return localStorage.getItem(onboardingStorageKey("complete")) === "1";
}

function completeOnboarding() {
  localStorage.setItem(onboardingStorageKey("complete"), "1");
  localStorage.removeItem(onboardingStorageKey("step"));
}

async function saveOnboardingPreferences(updates, { successMessage, nextStep } = {}) {
  if (!ensureLiveMode("Switch to Live to save real onboarding choices.")) {
    return false;
  }

  await fetchJson(`/v1/users/${encodeURIComponent(getUserId())}/preferences`, {
    method: "PATCH",
    body: updates,
  });
  if (nextStep) {
    setStoredOnboardingStep(nextStep);
  }
  await refreshExperience({ restoreScreen: false });
  if (successMessage) {
    showToast(successMessage);
  }
  return true;
}

function setSessionEntryFormLocked(locked, { allowMinutes = false } = {}) {
  elements.entryPointInput.readOnly = locked;
  elements.requestedMinutesInput.disabled = locked && !allowMinutes;
  elements.sessionGuideMode.disabled = locked;
  elements.textSourceSelect.disabled = locked;
}

function setSessionResumeMode(active) {
  [
    elements.entryPointInput?.closest("label"),
    elements.sessionGuideMode?.closest("label"),
    elements.textSourceSelect?.closest("label"),
  ].forEach((field) => {
    if (!field) {
      return;
    }
    field.classList.toggle("hidden", active);
  });
}

function updateSessionEntryState(activeSession) {
  const entryPanel = document.getElementById("session-entry-panel");
  const recommendationPanel = document.getElementById("recommendation-panel");
  if (recommendationPanel) recommendationPanel.classList.toggle("hidden", !!activeSession);
  if (activeSession) {
    if (entryPanel) entryPanel.classList.add("hidden");
    const session = activeSession.session;
    elements.sessionStatusPill.textContent = "Active";
    elements.entryPointInput.value = "continue where I left off";
    elements.requestedMinutesInput.value = session.requested_minutes || state.recommendation?.recommended_minutes || "";
    elements.sessionGuideMode.value = session.guide_mode || "";
    if (session.text_source_id) {
      elements.textSourceSelect.value = session.text_source_id;
    }
    setSessionResumeMode(true);
    setSessionEntryFormLocked(true, { allowMinutes: true });
    return;
  }

  if (entryPanel) entryPanel.classList.remove("hidden");
  setSessionResumeMode(false);
  setSessionEntryFormLocked(false);
  elements.sessionPanelHeading.textContent = "Start or continue";
  elements.sessionStatusPill.textContent = "Ready";
  elements.sessionFormCopy.textContent = state.recommendation
    ? `Emmaus suggests ${state.recommendation.recommended_minutes} minutes centered on ${humanizeFocusArea(state.recommendation.focus_area).toLowerCase()}.`
    : "Start a fresh guided session when you are ready.";
  elements.sessionFormButton.textContent = "Begin guided session";
  elements.entryPointInput.value = state.recommendation?.recommended_entry_point || "continue where I left off";
  elements.requestedMinutesInput.value = state.recommendation?.recommended_minutes || state.profile?.preferences?.preferred_session_minutes || "";
  elements.sessionGuideMode.value = "";
  const preferredSource = state.profile?.preferences?.preferred_translation_source_id;
  if (preferredSource) {
    elements.textSourceSelect.value = preferredSource;
  }
}
function buildTodayReasonSummary(recommendation) {
  if (!recommendation) {
    return "Emmaus is ready to guide you through a fresh session.";
  }

  const focusLabel = humanizeFocusArea(recommendation.focus_area).toLowerCase();
  const baseReason = truncateGuideCopy(polishGuideCopy(recommendation.reason), 150);
  const pattern = truncateGuideCopy(polishGuideCopy(safeArray(recommendation.gap_report?.observed_patterns)[0] || ""), 110);
  const isExplicitRevisit = /^Emmaus is (bringing you back|revisiting) /i.test(baseReason);

  if (isExplicitRevisit) {
    return baseReason;
  }
  if (focusLabel === "living it out") {
    return `Today Emmaus is helping you turn what you've studied into a clear next step.`;
  }
  if (focusLabel === "understanding the passage") {
    return `Today Emmaus is helping you slow down and understand the passage more clearly before moving on.`;
  }
  if (focusLabel === "steady rhythm") {
    return `Today Emmaus is helping you keep a steady study rhythm with one focused session.`;
  }
  if (baseReason) {
    return baseReason;
  }
  if (pattern) {
    return pattern;
  }
  return `Today Emmaus is helping you grow in ${focusLabel}.`;
}

function buildTodayCarryForwardCopy(memorySummary) {
  const carryForwardPrompt = memorySummary?.carry_forward_prompt;
  if (!carryForwardPrompt) {
    return "";
  }
  return truncateGuideCopy(polishGuideCopy(carryForwardPrompt), 135);
}
function renderTodayPlan(recommendation, activeSession, actionItems, memorySummary) {
  const openAction = actionItems.find((item) => item.status === "open");
  const carryForwardPrompt = memorySummary?.carry_forward_prompt || null;

  if (activeSession) {
    const session = activeSession.session;
    const nextQuestion = activeSession.current_question || session.questions?.[session.current_question_index] || null;
    const guideLabel = humanizeGuideMode(session.guide_mode).toLowerCase();
    const nextQuestionLabel = nextQuestion ? sentenceCase(nextQuestion.type).toLowerCase() : "next";
    const sessionSummary = nextQuestion
      ? `Pick up where you left off in ${formatReference(session.reference)}. Emmaus is guiding you in ${guideLabel} mode, and your next step is a ${nextQuestionLabel} question.`
      : `Pick up where you left off in ${formatReference(session.reference)}. Emmaus is guiding you in ${guideLabel} mode and helping you finish this session with focus.`;
    elements.todayPlanPill.textContent = "Resume";
    elements.todayPlanCard.dataset.action = "resume_session";
    elements.todayPlanCard.innerHTML = `
      <div class="today-plan-card">
        <p><strong>${escapeHtml(formatReference(session.reference))}</strong></p>
        <p class="today-plan-copy">${escapeHtml(sessionSummary)}</p>
        ${carryForwardPrompt ? `<p class="memory-prompt">${escapeHtml(carryForwardPrompt)}</p>` : ""}
        <div class="today-plan-actions">
          <span class="meta-pill">${escapeHtml(buildQuestionProgress(session))}</span>
          <span class="meta-pill">${escapeHtml(humanizeGuideMode(session.guide_mode))}</span>
        </div>
        <button class="primary-button full-width" type="button">Resume session</button>
      </div>
    `;
    return;
  }

  if (openAction) {
    elements.todayPlanPill.textContent = "Follow through";
    elements.todayPlanCard.dataset.action = "open_actions";
    elements.todayPlanCard.innerHTML = `
      <div class="today-plan-card">
        <p><strong>${escapeHtml(openAction.title)}</strong></p>
        <p class="today-plan-copy">${escapeHtml(openAction.detail)}</p>
        ${carryForwardPrompt ? `<p class="memory-prompt">${escapeHtml(carryForwardPrompt)}</p>` : ""}
        <div class="today-plan-actions">
          <span class="meta-pill">Created ${escapeHtml(formatDateTime(openAction.created_at))}</span>
          <span class="meta-pill">Next step</span>
        </div>
        <button class="primary-button full-width" type="button">Record what happened</button>
      </div>
    `;
    return;
  }

  if (recommendation) {
    elements.todayPlanPill.textContent = humanizeFocusArea(recommendation.focus_area);
    elements.todayPlanCard.dataset.action = "start_session";
    elements.todayPlanCard.innerHTML = `
      <div class="today-plan-card">
        <p><strong>${escapeHtml(formatReference(recommendation.recommended_reference))}</strong></p>
        <p class="today-plan-copy">${escapeHtml(recommendation.reason)}</p>
        ${carryForwardPrompt ? `<p class="memory-prompt"><strong>Keep building here:</strong> ${escapeHtml(carryForwardPrompt)}</p>` : ""}
        <div class="today-plan-actions">
          <span class="meta-pill">${escapeHtml(humanizeGuideMode(recommendation.recommended_guide_mode))}</span>
          <span class="meta-pill">${escapeHtml(String(recommendation.recommended_minutes))} min</span>
        </div>
        <p><strong>End with:</strong> ${escapeHtml(recommendation.suggested_action)}</p>
        <button class="primary-button full-width" type="button">Start today's plan</button>
      </div>
    `;
    return;
  }

  elements.todayPlanPill.textContent = "Set up";
  elements.todayPlanCard.dataset.action = "focus_identity";
  elements.todayPlanCard.innerHTML = `
    <div class="today-plan-card">
      <p><strong>Set your guide profile</strong></p>
      <p class="today-plan-copy">Add your rhythm and preferences so Emmaus can shape a better first study session.</p>
      <button class="primary-button full-width" type="button">Complete onboarding</button>
    </div>
  `;
}

function renderCompletionSummary(memorySummary, actionItems) {
  const anchorAction = state.lastFollowThroughUpdate?.actionItem
    || state.lastCompletion?.actionItem
    || actionItems.find((item) => item.action_item_id === state.selectedActionItemId)
    || actionItems[0]
    || null;

  if (!anchorAction && !memorySummary?.memory_count) {
    elements.completionSummaryPill.textContent = "Waiting";
    elements.completionSummaryCard.innerHTML = '<p class="empty-state">Complete a session and Emmaus will summarize what it noticed, what it is carrying forward, and your next step.</p>';
    return;
  }

  const followThroughUpdate = state.lastFollowThroughUpdate;
  const completionTag = followThroughUpdate ? "Updated" : state.lastCompletion ? "New" : "Ready";
  elements.completionSummaryPill.textContent = completionTag;
  const latestSummary = memorySummary?.latest_summary || "Emmaus is carrying a recent session forward.";
  const carryForwardPrompt = memorySummary?.carry_forward_prompt || null;
  const growthArea = safeArray(memorySummary?.growth_areas)[0] || null;
  const actionTitle = anchorAction?.title || "Your next action step";
  const actionDetail = anchorAction?.detail || "Emmaus will place your next step here after a session completes.";
  const actionCreatedAt = anchorAction?.created_at ? formatDateTime(anchorAction.created_at) : null;
  const followThroughNote = followThroughUpdate?.actionItem?.follow_up_note
    ? `<p class="session-context-copy"><strong>What landed:</strong> ${escapeHtml(followThroughUpdate.actionItem.follow_up_note)}</p>`
    : "";
  const activePrayer = state.prayerItems.find((item) => item.status === "active") || null;
  const prayerPrompt = activePrayer
    ? `Bring ${activePrayer.title} before Christ as you take this next step.`
    : "Ask Christ to help this passage move from reflection into obedience.";

  elements.completionSummaryCard.innerHTML = `
    <div class="completion-card">
      <p><strong>${followThroughUpdate ? "Emmaus updated this thread" : "Carry this with you today"}</strong></p>
      <p class="today-plan-copy">${escapeHtml(latestSummary)}</p>
      ${carryForwardPrompt ? `<p class="memory-prompt"><strong>Next thread:</strong> ${escapeHtml(carryForwardPrompt)}</p>` : ""}
      ${growthArea ? `<p><strong>Keep strengthening:</strong> ${escapeHtml(growthArea)}</p>` : ""}
      ${followThroughNote}
      <div class="inline-card">
        <p><strong>${escapeHtml(actionTitle)}</strong></p>
        <p>${escapeHtml(actionDetail)}</p>
        ${actionCreatedAt ? `<span class="meta-pill">Created ${escapeHtml(actionCreatedAt)}</span>` : ""}
        ${followThroughUpdate?.actionItem?.follow_up_outcome ? `<span class="meta-pill">${escapeHtml(sentenceCase(followThroughUpdate.actionItem.follow_up_outcome.replaceAll("_", " ")))}</span>` : ""}
      </div>
      <p class="session-context-copy"><strong>Close in prayer:</strong> ${escapeHtml(prayerPrompt)}</p>
    </div>
  `;
}

function renderActionItems(actionItems) {
  const openItems = actionItems.filter((item) => item.status === "open");
  elements.openActionCount.textContent = String(openItems.length);
  elements.openActionCopy.textContent = openItems.length
    ? `${openItems.length} next ${openItems.length === 1 ? "step is" : "steps are"} waiting for follow-through.`
    : "Your next step will show up here.";
  elements.actionSummaryPill.textContent = `${openItems.length} open`;

  syncSelectedActionItem(actionItems);

  if (!actionItems.length) {
    elements.actionItemList.innerHTML = '<p class="empty-state">No next steps yet. Complete a session and Emmaus will place your next step here.</p>';
    return;
  }

  const visibleItems = actionItems.slice(0, 2);
  const olderItems = actionItems.slice(2);
  const visibleMarkup = visibleItems.map((item) => buildActionItemCard(item)).join("");
  const olderMarkup = olderItems.length
    ? `
      <details class="review-history-details">
        <summary>Show ${olderItems.length} older next ${olderItems.length === 1 ? "step" : "steps"}</summary>
        <div class="review-history-details-body">
          ${olderItems.map((item) => buildActionItemCard(item)).join("")}
        </div>
      </details>
    `
    : "";

  elements.actionItemList.innerHTML = `
    <div class="list-stack">
      ${visibleMarkup}
      ${olderMarkup}
    </div>
  `;
}

function buildActionItemCard(item) {
  const isSelected = item.action_item_id === state.selectedActionItemId;
  const completed = item.status === "completed";
  const footer = completed
    ? `<p class="micro-copy">Completed ${escapeHtml(formatDateTime(item.completed_at))}${item.follow_up_outcome ? ` - ${escapeHtml(sentenceCase(item.follow_up_outcome.replaceAll("_", " ")) )}` : ""}</p>${item.follow_up_note ? `<p>${escapeHtml(item.follow_up_note)}</p>` : ""}`
    : `<button class="action-button" type="button" data-action-item-select="${escapeHtml(item.action_item_id)}">${isSelected ? "Selected for reflection" : "Record what happened"}</button>`;
  return `
    <article class="action-card ${completed ? "completed" : ""} ${isSelected ? "selected" : ""}">
      <div class="action-card-header">
        <div>
          <p><strong>${escapeHtml(item.title)}</strong></p>
          <p>${escapeHtml(item.detail)}</p>
        </div>
        <span class="status-pill">${escapeHtml(sentenceCase(item.status))}</span>
      </div>
      <p class="micro-copy">Created ${escapeHtml(formatDateTime(item.created_at))}</p>
      ${footer}
    </article>
  `;
}

function renderPrayerItems(prayerItems) {
  const activeItems = prayerItems.filter((item) => item.status === "active");
  elements.prayerSummaryPill.textContent = `${activeItems.length} active`;

  if (!prayerItems.length) {
    elements.prayerItemList.innerHTML = '<p class="empty-state">No prayer items yet. Add one here so Emmaus can keep it in view with your next steps.</p>';
    return;
  }

  elements.prayerItemList.innerHTML = prayerItems
    .map((item) => {
      const active = item.status === "active";
      const prayedCopy = item.last_prayed_at ? `Last prayed ${escapeHtml(formatDateTime(item.last_prayed_at))}` : "Not marked prayed yet";
      const answeredCopy = item.answered_at ? `<p class="micro-copy">Answered ${escapeHtml(formatDateTime(item.answered_at))}</p>` : "";
      const actions = active
        ? `<div class="button-row"><button class="action-button" type="button" data-prayer-pray="${escapeHtml(item.prayer_item_id)}">Prayed today</button><button class="action-button" type="button" data-prayer-answer="${escapeHtml(item.prayer_item_id)}">Mark answered</button></div>`
        : "";
      return `
        <article class="action-card ${active ? "" : "completed"}">
          <div class="action-card-header">
            <div>
              <p><strong>${escapeHtml(item.title)}</strong></p>
              <p>${escapeHtml(item.detail)}</p>
            </div>
            <span class="status-pill">${escapeHtml(item.status === "answered" ? "Answered" : "Active")}</span>
          </div>
          <p class="micro-copy">Created ${escapeHtml(formatDateTime(item.created_at))}</p>
          <p class="micro-copy">${prayedCopy}</p>
          ${answeredCopy}
          ${actions}
        </article>
      `;
    })
    .join("");
}

function renderReviewHistory(reviewHistory) {
  if (!elements.reviewHistoryCard || !elements.reviewSummaryPill) {
    return;
  }

  const sessions = safeArray(reviewHistory?.sessions);
  const prayers = safeArray(reviewHistory?.prayers);
  elements.reviewSummaryPill.textContent = sessions.length ? `${sessions.length} recent` : "Ready";

  if (!sessions.length && !prayers.length) {
    elements.reviewHistoryCard.innerHTML = '<p class="empty-state">Complete a few sessions and Emmaus will help you review your recent answers, next steps, and prayers here.</p>';
    return;
  }

  const visibleSessions = sessions.slice(0, 2);
  const olderSessions = sessions.slice(2);
  const sessionMarkup = visibleSessions.length
    ? visibleSessions.map((entry) => buildReviewSessionCard(entry)).join("")
    : '<p class="empty-state">No completed sessions yet. Your recent responses will show up here after you finish one.</p>';
  const olderSessionsMarkup = olderSessions.length
    ? `
      <details class="review-history-details">
        <summary>Show ${olderSessions.length} older review ${olderSessions.length === 1 ? "item" : "items"}</summary>
        <div class="review-history-details-body">
          ${olderSessions.map((entry) => buildReviewSessionCard(entry)).join("")}
        </div>
      </details>
    `
    : '';

  const prayerHistory = prayers.length
    ? `<div class="inline-card review-prayer-history"><p><strong>Prayer history</strong></p><p class="micro-copy">${escapeHtml(buildPrayerHistorySummary(prayers))}</p></div>`
    : '';

  elements.reviewHistoryCard.innerHTML = `
    <div class="list-stack review-history-stack">
      ${sessionMarkup}
      ${olderSessionsMarkup}
      ${prayerHistory}
    </div>
  `;
}

function buildReviewSessionCard(entry) {
  const session = entry?.session || null;
  if (!session) {
    return "";
  }

  const responses = safeArray(entry.responses).slice(0, 2);
  const responseMarkup = responses.length
    ? `<div class="review-response-list">${responses.map((response) => `
        <div class="inline-card review-response-card">
          <p><strong>${escapeHtml(humanizeQuestionType(response.question_type))}</strong></p>
          <p class="micro-copy">${escapeHtml(truncateGuideCopy(response.question, 100))}</p>
          <p>${escapeHtml(truncateGuideCopy(response.response_text, 150))}</p>
        </div>
      `).join("")}</div>`
    : '<p class="micro-copy">No saved responses for this session.</p>';

  const actionItem = entry.action_item;
  const actionMarkup = actionItem
    ? `<div class="inline-card review-action-card"><p><strong>Next step</strong></p><p>${escapeHtml(actionItem.title)}</p><p class="micro-copy">${escapeHtml(truncateGuideCopy(actionItem.detail, 140))}</p></div>`
    : '';

  const linkedPrayers = safeArray(entry.prayers);
  const prayerMarkup = linkedPrayers.length
    ? `<div class="inline-card review-prayer-card"><p><strong>Prayer carried with this session</strong></p><p>${escapeHtml(linkedPrayers[0].title)}</p><p class="micro-copy">${escapeHtml(truncateGuideCopy(linkedPrayers[0].detail, 140))}</p></div>`
    : '';

  const memoryMarkup = entry.memory?.summary
    ? `<p class="micro-copy">${escapeHtml(truncateGuideCopy(entry.memory.summary, 150))}</p>`
    : '';

  return `
    <article class="action-card review-session-card">
      <div class="action-card-header">
        <div>
          <p><strong>${escapeHtml(formatReference(session.reference))}</strong></p>
          <p class="micro-copy">Completed ${escapeHtml(formatDateTime(session.completed_at || session.started_at))}</p>
        </div>
        <span class="status-pill">${escapeHtml(humanizeGuideMode(session.guide_mode))}</span>
      </div>
      ${memoryMarkup}
      ${responseMarkup}
      ${actionMarkup}
      ${prayerMarkup}
    </article>
  `;
}

function buildPrayerHistorySummary(prayers) {
  const answeredCount = prayers.filter((item) => item.status === "answered").length;
  const activeCount = prayers.filter((item) => item.status === "active").length;
  const latest = prayers[0];
  const latestCopy = latest ? `Most recent: ${latest.title}.` : "";
  return `${activeCount} active, ${answeredCount} answered. ${latestCopy}`.trim();
}

function syncSelectedActionItem(actionItems) {
  const openItems = actionItems.filter((item) => item.status === "open");
  const selected = openItems.find((item) => item.action_item_id === state.selectedActionItemId) || openItems[0] || null;
  state.selectedActionItemId = selected?.action_item_id || null;

  if (!selected) {
    elements.followUpTargetCopy.textContent = "Choose an open next step above and record what happened.";
    elements.followUpSubmitButton.disabled = true;
    elements.followUpOutcomeSelect.value = "completed";
    elements.followUpNoteInput.value = "";
    return;
  }

  elements.followUpTargetCopy.textContent = `${selected.title}: ${selected.detail}`;
  elements.followUpSubmitButton.disabled = false;
  elements.followUpOutcomeSelect.value = selected.follow_up_outcome || "completed";
  elements.followUpNoteInput.value = selected.follow_up_note || "";
}

function buildSessionContextCard(payload) {
  const recommendation = payload.recommendation || state.recommendation;
  const memorySummary = state.memorySummary;
  const leadingPattern = safeArray(recommendation?.gap_report?.observed_patterns)[0] || null;
  const shortReason = buildPastoralSessionReason(recommendation, memorySummary);
  const shortPattern = leadingPattern ? truncateGuideCopy(polishGuideCopy(leadingPattern), 95) : null;
  const meta = [
    recommendation?.focus_area ? `<span class="meta-pill">${escapeHtml(humanizeFocusArea(recommendation.focus_area))}</span>` : "",
    recommendation?.recommended_minutes ? `<span class="meta-pill">${escapeHtml(String(recommendation.recommended_minutes))} min</span>` : "",
  ].filter(Boolean).join("");

  return `
    <div class="session-context-card">
      <p><strong>Why this passage today</strong></p>
      <p class="session-context-copy">${escapeHtml(shortReason)}</p>
      ${shortPattern ? `<p class="session-context-copy"><strong>Growth edge:</strong> ${escapeHtml(shortPattern)}</p>` : ""}
      ${meta ? `<div class="session-meta">${meta}</div>` : ""}
    </div>
  `;
}

function findRelevantSessionPrayer(payload) {
  const activePrayerItems = safeArray(state.prayerItems).filter((item) => item.status === "active");
  if (!activePrayerItems.length) {
    return null;
  }
  const sessionId = payload?.session?.session_id || null;
  return activePrayerItems.find((item) => item.related_session_id === sessionId) || activePrayerItems[0];
}

function buildSessionPrayerCard(payload) {
  const prayerItem = findRelevantSessionPrayer(payload);
  if (!prayerItem) {
    return `
      <div class="inline-card prayer-session-card">
        <p><strong>Pray before you continue</strong></p>
        <p class="session-context-copy">Ask Christ to open your eyes, steady your heart, and help you obey what this passage is saying.</p>
      </div>
    `;
  }

  const prayedCopy = prayerItem.last_prayed_at
    ? `Last prayed ${formatDateTime(prayerItem.last_prayed_at)}`
    : "Not marked prayed yet";
  const relatedCopy = prayerItem.related_session_id === payload?.session?.session_id
    ? "This prayer began in this session."
    : "Carry this prayer with you as you read and respond.";
  return `
    <div class="inline-card prayer-session-card">
      <p><strong>Carry this prayer into the session</strong></p>
      <p>${escapeHtml(prayerItem.title)}</p>
      <p class="session-context-copy">${escapeHtml(truncateGuideCopy(prayerItem.detail, 160))}</p>
      <p class="micro-copy">${escapeHtml(relatedCopy)} ${escapeHtml(prayedCopy)}</p>
      <div class="button-row">
        <button class="action-button" type="button" data-prayer-pray="${escapeHtml(prayerItem.prayer_item_id)}">Prayed today</button>
      </div>
    </div>
  `;
}

function sessionLengthLabel(minutes) {
  if (minutes <= 12) {
    return "Focused session";
  }
  if (minutes >= 23) {
    return "Deeper session";
  }
  return "Balanced session";
}

function buildSessionLengthCopy(session, commentaryNotes) {
  const minutes = Number(session?.requested_minutes || 0);
  const hasPassageHelps = commentaryNotes.some((note) => note?.metadata?.kind === "passage_helps");
  const hasCommentary = commentaryNotes.some((note) => note?.metadata?.kind === "commentary");
  if (minutes <= 12) {
    return "This shorter session keeps you close to the passage with two focused questions and one clear next step.";
  }
  if (minutes >= 23) {
    const extras = [];
    if (hasCommentary) {
      extras.push("commentary");
    }
    if (hasPassageHelps) {
      extras.push("passage helps");
    }
    const extrasCopy = extras.length ? `, with space to use ${extras.join(" and ")},` : "";
    return `This longer session gives you room for four questions${extrasCopy} and a more prayerful response at the end.`;
  }
  return "This session gives you enough space to read carefully, use passage helps, and work through three guided questions.";
}

function buildPastoralSessionReason(recommendation, memorySummary) {
  const focus = humanizeFocusArea(recommendation?.focus_area || "growth").toLowerCase();
  const carryForwardPrompt = memorySummary?.carry_forward_prompt ? truncateGuideCopy(polishGuideCopy(memorySummary.carry_forward_prompt), 100) : null;
  const reason = truncateGuideCopy(polishGuideCopy(recommendation?.reason || "Emmaus is helping you stay close to Christ in this passage."), 125);
  if (carryForwardPrompt) {
    return `Emmaus is bringing you back to ${focus} today so the last thread can deepen instead of getting left behind.`;
  }
  return reason;
}

function buildQuestionTransitionCopy(session, currentQuestion) {
  const latestMessage = polishGuideCopy(session?.latest_message || "").trim();
  const cleanedMessage = latestMessage.replace(/^Next question:\s*/i, "").trim();
  if (cleanedMessage && !/[.]{3}$/.test(cleanedMessage) && !/[\u2026]$/.test(cleanedMessage)) {
    return cleanedMessage;
  }
  if (!currentQuestion) {
    return "You've worked through the questions. Finish the session and let Emmaus help you carry one response into today.";
  }
  if (currentQuestion?.type === "observation") {
    return "Stay close to the passage and notice what it is saying before you move on.";
  }
  if (currentQuestion?.type === "interpretation") {
    return "Name what the passage means before you rush toward application.";
  }
  if (currentQuestion?.type === "application") {
    return "Let the passage shape one clear response you can carry into today.";
  }
  return "Take this next question slowly and stay close to the passage.";
}

function renderSessionStart(payload, { navigate = true } = {}) {
  state.activeSessionPayload = payload;
  state.currentQuestion = payload.current_question || null;

  const session = payload.session;
  const commentaryNotes = safeArray(payload.commentary);
  const guideIntro = state.currentQuestion
    ? `Emmaus will guide this session one question at a time, starting with ${humanizeQuestionType(state.currentQuestion.type).toLowerCase()}.`
    : "Emmaus is ready to guide this session one step at a time as you read and respond.";
  const lengthIntro = buildSessionLengthCopy(session, commentaryNotes);
  const guideLabelMap = {
    guide: "How this session will work",
    peer: "How this session will work",
    challenger: "How this session will work",
    coach: "How this session will work",
  };
  const guideLabel = guideLabelMap[session.guide_mode] || sentenceCase(session.guide_mode);
  elements.sessionStatusPill.textContent = sentenceCase(session.status);
  const referenceText = formatReference(session.reference);
  elements.sessionReference.textContent = referenceText;
  if (elements.passageReference) {
    elements.passageReference.textContent = referenceText;
    elements.passageReference.hidden = !referenceText;
  }
  elements.questionProgressPill.textContent = buildQuestionProgress(session);
  elements.sessionHero.innerHTML = `
    ${buildSessionContextCard(payload)}
    ${buildSessionPrayerCard(payload)}
    <div class="inline-card">
      <p><strong>${escapeHtml(guideLabel)}</strong></p>
      <p>${escapeHtml(guideIntro)}</p>
      <p class="session-context-copy">${escapeHtml(lengthIntro)}</p>
      <div class="session-meta">
        <span class="meta-pill">${escapeHtml(String(session.requested_minutes))} min</span>
        <span class="meta-pill">${escapeHtml(sessionLengthLabel(session.requested_minutes))}</span>
      </div>
    </div>
  `;
  elements.passageText.innerHTML = buildPassageMarkup(payload.passage);
  elements.sessionPlan.innerHTML = safeArray(session.plan).length
    ? safeArray(session.plan)
        .map(
          (step) => `
            <div class="inline-card">
              <p><strong>${escapeHtml(step.title)}</strong></p>
              <p>${escapeHtml(step.instruction)}</p>
              <span class="meta-pill">${escapeHtml(String(step.estimated_minutes))} min</span>
            </div>
          `,
        )
        .join("")
    : '<p class="empty-state">No study plan is available yet.</p>';
  elements.commentaryBlock.innerHTML = buildCommentaryMarkup(commentaryNotes);

  elements.questionTransitionCopy.textContent = buildQuestionTransitionCopy(session, state.currentQuestion);
  if (state.currentQuestion) {
    elements.currentQuestionHeading.textContent = humanizeQuestionType(state.currentQuestion.type);
    elements.currentQuestionCopy.textContent = state.currentQuestion.question;
    elements.responseText.disabled = false;
    elements.engagementInput.disabled = false;
    elements.submitResponseButton.disabled = false;
  } else {
    elements.currentQuestionHeading.textContent = "Current question";
    elements.currentQuestionCopy.textContent = "You have completed the main questions. Finish the session to receive your action step.";
    elements.responseText.disabled = true;
    elements.engagementInput.disabled = true;
    elements.submitResponseButton.disabled = true;
  }

  updateSessionEntryState(payload);
  refreshStudyNotes().catch(handleError);

  if (navigate) {
    showScreen("session");
  }
}

function clearSessionView() {
  state.activeSessionPayload = null;
  state.currentQuestion = null;
  elements.sessionReference.textContent = "No active session yet";
  if (elements.passageReference) {
    elements.passageReference.textContent = "";
    elements.passageReference.hidden = true;
  }
  elements.questionProgressPill.textContent = "Questions unavailable";
  elements.sessionHero.innerHTML = '<p class="empty-state">Start a session to see the passage, plan, and first question.</p>';
  elements.passageText.innerHTML = "Start a session to see the passage, plan, and first question.";
  elements.sessionPlan.innerHTML = '<p class="empty-state">Your study plan will appear here once a session starts.</p>';
  elements.commentaryBlock.innerHTML = "";
  elements.currentQuestionHeading.textContent = "Current question";
  elements.questionTransitionCopy.textContent = "Emmaus will guide you one step at a time.";
  elements.currentQuestionCopy.textContent = "Emmaus will place the next question here.";
  elements.responseText.value = "";
  elements.responseText.disabled = true;
  elements.engagementInput.value = 4;
  elements.engagementInput.disabled = true;
  elements.submitResponseButton.disabled = true;
  refreshStudyNotes().catch(handleError);
}

function renderTurnResponse(payload) {
  if (!state.activeSessionPayload) {
    return;
  }
  state.activeSessionPayload = {
    ...state.activeSessionPayload,
    session: payload.session,
    current_question: payload.next_question || null,
  };
  state.currentQuestion = payload.next_question || null;
  elements.responseText.value = "";
  renderSessionStart(state.activeSessionPayload, { navigate: false });
}

async function loadNudgeArtifacts(previewAt = null) {
  if (isDemoMode()) {
    renderNudge(state.nudge, state.nudgePlan);
    return;
  }

  const payload = { user_id: getUserId() };
  if (previewAt) {
    payload.preview_at = previewAt;
  }

  const [preview, plan] = await Promise.all([
    fetchJson("/v1/agent/nudges/preview", { method: "POST", body: payload }),
    fetchJson("/v1/agent/nudges/plan", { method: "POST", body: payload }),
  ]);

  state.nudge = preview;
  state.nudgePlan = plan;
  renderNudge(preview, plan);
}

function buildCommentaryMarkup(commentaryNotes) {
  if (!commentaryNotes.length) {
    return "";
  }

  const passageHelpNotes = commentaryNotes.filter((note) => note?.metadata?.kind === "passage_helps");
  const commentaryOnlyNotes = commentaryNotes.filter((note) => note?.metadata?.kind !== "passage_helps");
  const blocks = [];

  if (commentaryOnlyNotes.length) {
    blocks.push(buildCommentaryNotesMarkup(commentaryOnlyNotes));
  }
  if (passageHelpNotes.length) {
    blocks.push(buildPassageHelpsMarkup(passageHelpNotes));
  }

  return blocks.join("");
}

function buildCommentaryNotesMarkup(commentaryNotes) {
  const notesMarkup = commentaryNotes
    .map((note) => {
      const sourceName = note?.metadata?.source_name || "Commentary";
      const heading = note?.title ? `${sourceName}: ${note.title}` : sourceName;
      return `
        <div class="commentary-note scripture-adjacent-note">
          <p><strong>${escapeHtml(heading)}</strong></p>
          <p>${escapeHtml(note.body)}</p>
          ${note?.metadata?.source_name ? `<span class="meta-pill">${escapeHtml(note.metadata.source_name)}</span>` : ""}
        </div>
      `;
    })
    .join("");
  return `
    <p class="micro-copy commentary-handoff">Before you answer, let this note help you linger over the passage a little longer.</p>
    ${notesMarkup}
  `;
}

function buildPassageHelpsMarkup(commentaryNotes) {
  const sections = commentaryNotes
    .map((note, index) => {
      const section = String(note?.metadata?.section || "summary");
      const items = buildCommentaryNoteItems(note.body, section);
      const bodyMarkup = items.length > 1
        ? `<ul class="commentary-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
        : `<p>${escapeHtml(items[0] || note.body)}</p>`;
      return `
        <details class="commentary-details" ${index === 0 ? "open" : ""}>
          <summary>
            <span>${escapeHtml(humanizeCommentarySection(section))}</span>
            <span class="meta-pill">${escapeHtml(note.title)}</span>
          </summary>
          <div class="commentary-details-body">
            ${bodyMarkup}
          </div>
        </details>
      `;
    })
    .join("");

  return `<div class="commentary-section-stack scripture-adjacent-helps">${sections}</div>`;
}

function buildCommentaryNoteItems(body, section) {
  const cleaned = String(body || "").trim();
  if (!cleaned) {
    return [];
  }

  if (section === "headings") {
    return cleaned
      .replace(/^Section headings in the ESV:\s*/i, "")
      .split(/\s*;\s*/)
      .map((item) => item.trim())
      .filter(Boolean);
  }

  if (section === "crossrefs") {
    return cleaned
      .replace(/^See\s+/i, "")
      .split(/\s*;\s*/)
      .map((item) => item.trim().replace(/[.]$/, ""))
      .filter(Boolean);
  }

  return [cleaned];
}

function humanizeCommentarySection(value) {
  const normalized = String(value || "summary").replaceAll("_", " ");
  if (normalized === "crossrefs") {
    return "Cross-references";
  }
  if (normalized === "footnotes") {
    return "Footnotes";
  }
  if (normalized === "headings") {
    return "Headings";
  }
  if (normalized === "summary") {
    return "From the ESV";
  }
  return sentenceCase(normalized);
}

function renderNudge(nudge, nudgePlan) {
  const statusCopy = nudgePlan?.delivery_status ? sentenceCase(nudgePlan.delivery_status.replaceAll("_", " ")) : sentenceCase(nudge?.timing_decision || "checking");
  elements.nudgeTimingPill.textContent = statusCopy;

  if (!nudge) {
    elements.nudgeCard.innerHTML = '<p class="empty-state">No reminder preview is available right now.</p>';
    elements.nudgePlanCard.innerHTML = '<p class="empty-state">Delivery planning will appear here after the preview is generated.</p>';
    return;
  }

  const threadContext = buildNudgeThreadContext(nudge);
  elements.nudgeCard.innerHTML = `
    <div class="nudge-card">
      <p><strong>${escapeHtml(nudge.title)}</strong></p>
      <p>${escapeHtml(nudge.message)}</p>
      ${threadContext}
      <div class="nudge-meta">
        <span class="meta-pill">${escapeHtml(humanizeNudgeType(nudge.nudge_type))}</span>
        <span class="meta-pill">${escapeHtml(String(nudge.recommended_minutes))} min</span>
        <span class="meta-pill">${escapeHtml(humanizeGuideMode(nudge.recommended_guide_mode))}</span>
      </div>
      <p><strong>Timing:</strong> ${escapeHtml(nudge.timing_reason)}</p>
      ${nudge.scheduled_for ? `<p><strong>Scheduled for:</strong> ${escapeHtml(formatDateTime(nudge.scheduled_for, nudge.local_timezone))}</p>` : ""}
    </div>
  `;

  if (!nudgePlan) {
    elements.nudgePlanCard.innerHTML = '<p class="empty-state">A delivery plan is not available yet.</p>';
    return;
  }

  elements.nudgePlanCard.innerHTML = `
    <div class="nudge-plan-card">
      <p><strong>Delivery plan</strong></p>
      <div class="nudge-meta">
        <span class="meta-pill">${escapeHtml(sentenceCase(nudgePlan.delivery_status.replaceAll("_", " ")) )}</span>
        <span class="meta-pill">${escapeHtml(sentenceCase(nudgePlan.delivery_channel.replaceAll("_", " ")) )}</span>
      </div>
      <p>${escapeHtml(nudgePlan.reason)}</p>
      ${nudgePlan.deliver_at ? `<p><strong>Deliver at:</strong> ${escapeHtml(formatDateTime(nudgePlan.deliver_at, nudge.local_timezone))}</p>` : ""}
      ${nudgePlan.fallback_at ? `<p><strong>Fallback:</strong> ${escapeHtml(formatDateTime(nudgePlan.fallback_at, nudge.local_timezone))}</p>` : ""}
    </div>
  `;
}

function buildNudgeThreadContext(nudge) {
  const memorySummary = state.memorySummary;
  const latestCompletedAction = Array.isArray(state.actionItems)
    ? state.actionItems.find((item) => item.status === "completed" && (item.follow_up_outcome || item.completed_at))
    : null;

  if (!memorySummary?.carry_forward_prompt && !latestCompletedAction) {
    return "";
  }

  const reasonLine = latestCompletedAction
    ? `Because you already followed through on ${escapeHtml(latestCompletedAction.title)}, Emmaus is carrying that thread forward instead of starting over.`
    : "Emmaus is carrying one recent thread forward so this nudge feels specific instead of generic.";

  const followThroughLine = latestCompletedAction?.follow_up_note
    ? `<p class="micro-copy">Last follow-through: ${escapeHtml(latestCompletedAction.follow_up_note)}</p>`
    : "";

  const promptLine = memorySummary?.carry_forward_prompt
    ? `<p><strong>Carry forward:</strong> ${escapeHtml(memorySummary.carry_forward_prompt)}</p>`
    : "";

  return `
    <div class="nudge-thread-card">
      <p class="panel-label">Why Emmaus is reaching out</p>
      <p>${reasonLine}</p>
      ${followThroughLine}
      ${promptLine}
    </div>
  `;
}

function renderDemoControls() {
  const label = DEMO_SCENARIO_LABELS[state.demoScenario] || DEMO_SCENARIO_LABELS.first_visit;
  elements.demoStatusCopy.textContent = isDemoMode()
    ? `Currently previewing ${label}. Demo scenes are read-only and never write to your live Emmaus data.`
    : "Live mode is using the real API-backed data for the current user. Switch to a seeded demo scene anytime.";
  if (elements.demoSceneDetail) {
    elements.demoSceneDetail.innerHTML = `
      <p><strong>${escapeHtml(isDemoMode() ? `Previewing ${label}` : "Current view")}</strong></p>
      <p class="micro-copy">${escapeHtml(DEMO_SCENARIO_DETAILS[state.demoScenario] || DEMO_SCENARIO_DETAILS.live)}</p>
    `;
  }

  elements.demoSceneRow.querySelectorAll("[data-demo-scenario]").forEach((button) => {
    const isSelected = button.dataset.demoScenario === state.demoScenario;
    button.classList.toggle("choice-chip-active", isSelected);
    button.setAttribute("aria-pressed", isSelected ? "true" : "false");
  });
}
async function onDemoScenarioSelect(event) {
  const button = event.target.closest("[data-demo-scenario]");
  if (!button) {
    return;
  }

  const scenario = normalizeDemoScenario(button.dataset.demoScenario);
  if (!scenario || scenario === state.demoScenario) {
    return;
  }

  state.demoScenario = scenario;
  localStorage.setItem("emmaus.demoScenario", scenario);
  syncDemoQueryParam(scenario);
  await loadTextSources();
  await refreshExperience({ restoreScreen: false });
  showScreen("home");
  showToast(isDemoMode() ? `Previewing ${DEMO_SCENARIO_LABELS[scenario]}.` : "Switched back to live data.");
}

async function onHeroPrimaryAction() {
  await onTodayPlanAction();
}

async function onTodayPlanAction() {
  const action = elements.todayPlanCard.dataset.action;
  if (action === "resume_session") {
    showScreen("session");
    return;
  }
  if (action === "open_actions") {
    showScreen("actions");
    return;
  }
  if (action === "focus_identity") {
    focusIdentityForm();
    return;
  }
  if (action === "start_session") {
    await startGuidedSession();
    return;
  }
  showScreen("session");
}

async function onOnboardingAction(event) {
  const button = event.target.closest("[data-action]");
  if (!button) {
    return;
  }

  const action = button.dataset.action;
  if (action === "focus-identity") {
    focusIdentityForm();
    return;
  }
  if (action === "onboarding-use-starter") {
    setStoredOnboardingStep(2);
    await setPreferredBibleSource(STARTER_SOURCE_ID, { successMessage: "Starter Bible selected." });
    return;
  }
  if (action === "onboarding-use-esv") {
    const esvSource = getSourceById(ESV_SOURCE_ID);
    if (esvSource) {
      setStoredOnboardingStep(2);
      await setPreferredBibleSource(ESV_SOURCE_ID, { successMessage: "ESV selected." });
      return;
    }
    onFocusEsvSource();
    return;
  }
  if (action === "onboarding-focus-upload") {
    const uploadForm = document.getElementById("source-upload-form");
    uploadForm?.scrollIntoView({ behavior: "smooth", block: "center" });
    document.getElementById("source-upload-name")?.focus();
    return;
  }
  if (action === "onboarding-focus-advanced") {
      const sourceUi = bibleSourceElements();
      if (!state.bibleSetupExpanded) {
        onToggleAdvancedBibleSetup();
      }
      sourceUi.advancedPanel?.scrollIntoView({ behavior: "smooth", block: "center" });
      sourceUi.apiName?.focus();
      return;
    }
  if (action === "onboarding-set-minutes") {
    const minutes = optionalNumber(button.dataset.minutes);
    if (!minutes) {
      return;
    }
    elements.preferredMinutesInput.value = String(minutes);
    elements.requestedMinutesInput.value = String(minutes);
    await saveOnboardingPreferences(
      { preferred_session_minutes: minutes },
      { successMessage: `Emmaus will plan around ${minutes} minutes.`, nextStep: 3 },
    );
    return;
  }
  if (action === "onboarding-set-window") {
    const presets = {
      morning: { preferred_study_window_start: "07:00", preferred_study_window_end: "09:00" },
      midday: { preferred_study_window_start: "12:00", preferred_study_window_end: "14:00" },
      evening: { preferred_study_window_start: "19:00", preferred_study_window_end: "21:00" },
    };
    const preset = presets[button.dataset.window];
    if (!preset) {
      return;
    }
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || optionalText(elements.timezoneInput.value) || "UTC";
    elements.timezoneInput.value = timezone;
    elements.studyWindowStartInput.value = preset.preferred_study_window_start;
    elements.studyWindowEndInput.value = preset.preferred_study_window_end;
    state.selectedStudyDays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
    updateStudyDayChips();
    await saveOnboardingPreferences(
      {
        timezone,
        preferred_study_days: state.selectedStudyDays,
        preferred_study_window_start: preset.preferred_study_window_start,
        preferred_study_window_end: preset.preferred_study_window_end,
      },
      { successMessage: `Emmaus will aim for ${sentenceCase(button.dataset.window)} sessions.`, nextStep: 4 },
    );
    return;
  }
  if (action === "onboarding-start-session") {
    await startGuidedSession({ fromOnboarding: true });
    return;
  }
  showScreen("session");
}

function onActionListClick(event) {
  const button = event.target.closest("[data-action-item-select]");
  if (!button) {
    return;
  }
  state.selectedActionItemId = button.dataset.actionItemSelect;
  renderActionItems(state.actionItems);
}

async function onPrayerListClick(event) {
  const prayButton = event.target.closest("[data-prayer-pray]");
  const answerButton = event.target.closest("[data-prayer-answer]");
  if (!prayButton && !answerButton) {
    return;
  }
  if (!ensureLiveMode("Switch to Live to update a real prayer item.")) {
    return;
  }

  const prayerItemId = prayButton?.dataset.prayerPray || answerButton?.dataset.prayerAnswer;
  const endpoint = prayButton ? "pray" : "answer";
  await fetchJson(`/v1/study/prayer-items/${encodeURIComponent(prayerItemId)}/${endpoint}`, {
    method: "POST",
    body: { user_id: getUserId() },
  });
  const destinationScreen = state.activeScreen === "session" ? "session" : "actions";
  await refreshExperience({ restoreScreen: false });
  showScreen(destinationScreen);
  showToast(prayButton ? "Prayer updated." : "Prayer marked answered.");
}

async function onSubmitPrayerItem(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to save a real prayer item.")) {
    return;
  }

  const title = optionalText(elements.prayerTitleInput.value);
  const detail = optionalText(elements.prayerDetailInput.value);
  if (!title || !detail) {
    showToast("Add both a prayer title and what you want to pray for.");
    return;
  }

  await fetchJson("/v1/study/prayer-items", {
    method: "POST",
    body: {
      user_id: getUserId(),
      title,
      detail,
      related_session_id: state.activeSessionPayload?.session?.session_id || null,
    },
  });
  elements.prayerTitleInput.value = "";
  elements.prayerDetailInput.value = "";
  await refreshExperience({ restoreScreen: false });
  showScreen("actions");
  showToast("Prayer item saved.");
}

async function onSaveIdentity(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to save real preferences.")) {
    return;
  }

  const userId = getUserId();
  state.userId = userId;
  localStorage.setItem("emmaus.userId", userId);
  const payload = {
    display_name: optionalText(elements.displayNameInput.value),
    preferred_session_minutes: optionalNumber(elements.preferredMinutesInput.value),
    preferred_guide_mode: optionalText(elements.guideModeSelect.value),
    preferred_question_style: optionalText(elements.questionStyleSelect.value),
    preferred_guidance_tone: optionalText(elements.guidanceToneSelect.value),
    preferred_translation_source_id: optionalText(elements.preferredSourceSelect.value),
    nudge_intensity: optionalText(elements.nudgeIntensitySelect.value),
    timezone: optionalText(elements.timezoneInput.value) || "America/New_York",
    preferred_study_days: state.selectedStudyDays,
    preferred_study_window_start: optionalText(elements.studyWindowStartInput.value),
    preferred_study_window_end: optionalText(elements.studyWindowEndInput.value),
    quiet_hours_start: optionalText(elements.quietHoursStartInput.value),
    quiet_hours_end: optionalText(elements.quietHoursEndInput.value),
  };

  await fetchJson(`/v1/users/${encodeURIComponent(userId)}/preferences`, {
    method: "PATCH",
    body: payload,
  });
  await refreshExperience({ restoreScreen: false });
  showToast("Preferences saved.");
}

async function onSaveMood(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to save a mood check-in.")) {
    return;
  }

  await fetchJson("/v1/study/mood", {
    method: "POST",
    body: {
      user_id: getUserId(),
      mood: state.selectedMood,
      energy: elements.energySelect.value,
      notes: optionalText(elements.moodNotes.value),
    },
  });
  await refreshExperience({ restoreScreen: false });
  showToast("Mood check-in saved.");
}

async function onStartSession(event) {
  event.preventDefault();
  await startGuidedSession();
}

async function startGuidedSession({ fromOnboarding = false } = {}) {
  if (isDemoMode()) {
    showScreen("session");
    showToast("Demo mode is read-only. Switch to Live to start a real session.");
    return;
  }

  if (state.activeSessionPayload?.session?.status === "active") {
    const activeSession = state.activeSessionPayload.session;
    const requestedMinutes = optionalNumber(elements.requestedMinutesInput.value) || activeSession.requested_minutes;
    const payload = await fetchJson("/v1/agent/session/update", {
      method: "POST",
      body: {
        session_id: activeSession.session_id,
        user_id: getUserId(),
        requested_minutes: requestedMinutes,
      },
    });
    if (fromOnboarding) {
      completeOnboarding();
    }
    state.recommendation = payload.recommendation;
    renderSessionStart(payload, { navigate: true });
    renderTodayPlan(state.recommendation, payload, state.actionItems, state.memorySummary);
    showToast(requestedMinutes === activeSession.requested_minutes ? "Session resumed." : `Emmaus adjusted the rest of this session for about ${requestedMinutes} minutes.`);
    return;
  }

  const payload = await fetchJson("/v1/agent/session/start", {
    method: "POST",
    body: {
      user_id: getUserId(),
      display_name: optionalText(elements.displayNameInput.value),
      entry_point: optionalText(elements.entryPointInput.value) || state.recommendation?.recommended_entry_point || "continue where I left off",
      requested_minutes: optionalNumber(elements.requestedMinutesInput.value),
      guide_mode: optionalText(elements.sessionGuideMode.value),
      text_source_id: optionalText(elements.textSourceSelect.value),
    },
  });

  if (fromOnboarding) {
    completeOnboarding();
  }
  state.recommendation = payload.recommendation;
  renderSessionStart(payload, { navigate: true });
  renderTodayPlan(state.recommendation, payload, state.actionItems, state.memorySummary);
  showToast(fromOnboarding ? "Your first session is ready." : "Session started.");
}

async function onSubmitResponse(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to send a real study response.")) {
    return;
  }
  if (!state.activeSessionPayload?.session?.session_id) {
    showToast("Start or resume a session first.");
    return;
  }

  const responseText = optionalText(elements.responseText.value);
  if (!responseText) {
    showToast("Add a response before sending it.");
    return;
  }

  const payload = await fetchJson("/v1/agent/session/respond", {
    method: "POST",
    body: {
      session_id: state.activeSessionPayload.session.session_id,
      user_id: getUserId(),
      response_text: responseText,
      engagement_score: optionalNumber(elements.engagementInput.value) || 4,
    },
  });

  renderTurnResponse(payload);
  showToast(payload.next_question ? "Response saved. Emmaus has the next question ready." : "Response saved. You can complete the session now.");
}

async function onCompleteSession(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to complete a real session.")) {
    return;
  }
  if (!state.activeSessionPayload?.session?.session_id) {
    showToast("Start or resume a session before completing it.");
    return;
  }

  const payload = await fetchJson("/v1/agent/session/complete", {
    method: "POST",
    body: {
      session_id: state.activeSessionPayload.session.session_id,
      user_id: getUserId(),
      summary_notes: optionalText(elements.summaryNotes.value),
      action_item_title: optionalText(elements.actionItemTitle.value),
      action_item_detail: optionalText(elements.actionItemDetail.value),
      engagement_score: optionalNumber(elements.engagementInput.value) || 4,
    },
  });

  state.lastFollowThroughUpdate = null;
  state.lastCompletion = {
    actionItem: payload.action_item,
    engagement: payload.engagement,
    session: payload.session,
    completedAt: new Date().toISOString(),
  };
  state.selectedActionItemId = payload.action_item.action_item_id;
  elements.summaryNotes.value = "";
  elements.actionItemTitle.value = "";
  elements.actionItemDetail.value = "";
  await refreshExperience({ restoreScreen: false });
  showScreen("actions");
  showToast("Session completed. Your next step is ready.");
}

async function onSubmitActionFollowUp(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to save a real follow-through note.")) {
    return;
  }
  if (!state.selectedActionItemId) {
    showToast("Choose a next step first.");
    return;
  }

  const beforeMemorySummary = state.memorySummary ? JSON.parse(JSON.stringify(state.memorySummary)) : null;
  const updatedActionItem = await fetchJson(`/v1/study/action-items/${encodeURIComponent(state.selectedActionItemId)}/complete`, {
    method: "POST",
    body: {
      user_id: getUserId(),
      follow_up_note: optionalText(elements.followUpNoteInput.value),
      follow_up_outcome: optionalText(elements.followUpOutcomeSelect.value),
    },
  });

  elements.followUpNoteInput.value = "";
  await refreshExperience({ restoreScreen: false });
  state.lastFollowThroughUpdate = {
    actionItem: updatedActionItem,
    beforeMemorySummary,
    afterMemorySummary: state.memorySummary ? JSON.parse(JSON.stringify(state.memorySummary)) : null,
  };
  renderCompletionSummary(state.memorySummary, state.actionItems);
  showScreen("actions");
  showToast("You saved what happened, and Emmaus updated your thread.");
}

async function onSubmitLookBack(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to save a real look-back reflection.")) {
    return;
  }
  const prompt = state.lookBack?.prompt;
  if (!prompt) {
    showToast("There is not a look-back prompt ready right now.");
    return;
  }
  const responseText = optionalText(elements.lookBackResponseText.value);
  if (!responseText) {
    showToast("Add a short reflection before saving it.");
    return;
  }

  const review = await fetchJson("/v1/study/look-back/respond", {
    method: "POST",
    body: {
      user_id: getUserId(),
      session_id: prompt.session_id,
      response_text: responseText,
    },
  });

  elements.lookBackResponseText.value = "";
  await refreshExperience({ restoreScreen: false });
  showScreen("home");
  showToast(review.outcome === "clear" ? "Emmaus saved that look-back clearly." : "Emmaus saved that look-back and will keep reinforcing the thread.");
}

async function onPreviewNudgeAtTime(event) {
  event.preventDefault();
  const previewAt = normalizePreviewAt(elements.previewAtInput.value);
  if (isDemoMode()) {
    renderNudge(state.nudge, state.nudgePlan);
    showToast("Demo mode is showing a seeded nudge plan.");
    return;
  }
  await loadNudgeArtifacts(previewAt);
  showToast(previewAt ? "Reminder timing refreshed for the selected time." : "Reminder timing refreshed.");
}

function selectMood(mood) {
  state.selectedMood = mood;
  elements.moodChipRow.querySelectorAll(".choice-chip").forEach((chip) => {
    chip.classList.toggle("choice-chip-active", chip.dataset.value === mood);
  });
}

function toggleStudyDay(day) {
  if (!day) {
    return;
  }
  if (state.selectedStudyDays.includes(day)) {
    state.selectedStudyDays = state.selectedStudyDays.filter((value) => value !== day);
  } else {
    state.selectedStudyDays = [...state.selectedStudyDays, day];
  }
  updateStudyDayChips();
}

function updateStudyDayChips() {
  elements.studyDaysRow.querySelectorAll(".choice-chip").forEach((chip) => {
    chip.classList.toggle("choice-chip-active", state.selectedStudyDays.includes(chip.dataset.day));
  });
}

function restorePreferredScreen() {
  const desiredScreen = state.activeScreen || "home";
  if (desiredScreen === "session" && !state.activeSessionPayload) {
    showScreen("home");
    return;
  }
  showScreen(desiredScreen);
}

function showScreen(screenName) {
  if (screenName === "memorize") screenName = "session";
  state.activeScreen = screenName;
  localStorage.setItem("emmaus.activeScreen", screenName);
  const memorizeUnderStudy = screenName === "session";
  elements.screens.forEach((screen) => {
    const target = screen.dataset.screen;
    const isActive = target === screenName || (memorizeUnderStudy && target === "memorize");
    screen.classList.toggle("screen-active", isActive);
  });
  elements.navButtons.forEach((button) => {
    button.classList.toggle("nav-pill-active", button.dataset.navTarget === screenName);
  });
  resetViewportScroll();
  if (screenName === "session") {
    loadMemorizeScreen().catch(handleError);
  }
}

function resetViewportScroll() {
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  document.documentElement.scrollTop = 0;
  document.body.scrollTop = 0;
}

function focusIdentityForm() {
  showScreen("profile");
  if (!elements.onboardingPanel.classList.contains("hidden")) {
    elements.onboardingPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  elements.identityForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

function openBibleSettingsInProfile() {
  showScreen("profile");
  setBibleManagerExpanded(true);
  elements.profileBiblePanel?.scrollIntoView({ behavior: "smooth", block: "start" });
  elements.sourceManageToggle?.focus();
}

function syncDemoQueryParam(scenario) {
  const url = new URL(window.location.href);
  if (scenario === "live") {
    url.searchParams.delete("demo");
  } else {
    url.searchParams.set("demo", scenario);
  }
  window.history.replaceState({}, "", url);
}

function ensureLiveMode(message) {
  if (!isDemoMode()) {
    return true;
  }
  showToast(message);
  return false;
}

function getUserId() {
  return optionalText(elements.userIdInput.value) || state.userId || "demo-user";
}

function optionalText(value) {
  const normalized = typeof value === "string" ? value.trim() : "";
  return normalized || null;
}

function optionalNumber(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function normalizePreviewAt(value) {
  if (!value) {
    return null;
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
}

async function fetchJson(url, { method = "GET", body = null, headers = {}, allowNull = false } = {}) {
  const response = await fetch(url, {
    method,
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    if (allowNull && response.status === 404) {
      return null;
    }
    let detail = `Request failed with status ${response.status}.`;
    try {
      const payload = await response.json();
      if (typeof payload?.detail === "string") {
        detail = payload.detail;
      } else if (Array.isArray(payload?.detail)) {
        detail = payload.detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
      }
    } catch {
      // Leave the fallback detail in place.
    }
    throw new Error(detail);
  }

  const text = await response.text();
  if (!text) {
    return null;
  }
  const payload = JSON.parse(text);
  return allowNull && payload === null ? null : payload;
}

function handleError(error) {
  const message = error instanceof Error ? error.message : "Something went wrong.";
  showToast(message);
}

const memorizeState = {
  verses: [],
  progress: null,
  drill: null,
};

const notesState = {
  notes: [],
  reference: null,
};

const MEMORIZE_DRILL_STAGES = [
  { label: "Full verse" },
  { label: "Every third word hidden" },
  { label: "First letter cues" },
  { label: "First letters only" },
  { label: "Reference + first word" },
];

function bindMemorizeEvents() {
  document.getElementById("memorize-add-verse-form")?.addEventListener("submit", onAddMemorizedVerse);
  document.getElementById("memorize-target-form")?.addEventListener("submit", onCreateMemorizationTarget);
  document.getElementById("memorize-start-review-button")?.addEventListener("click", onStartMemorizationReview);
  document.getElementById("memorize-drill-submit")?.addEventListener("click", onMemorizeDrillSubmit);
  document.getElementById("memorize-drill-exit")?.addEventListener("click", exitMemorizationDrill);
  document.getElementById("memorize-verse-list")?.addEventListener("click", onMemorizeVerseListClick);
  document.getElementById("memorize-drill-rating-row")?.addEventListener("click", onMemorizeRatingClick);
  bindVersePickerEvents();
}

const versePickerState = {
  activeTab: "reference",
  themeLoaded: false,
  navesLoaded: false,
  booksLoaded: false,
  selectedBook: null,
  selectedChapter: null,
};

function bindVersePickerEvents() {
  document.querySelectorAll(".verse-picker-tab").forEach((tab) => {
    tab.addEventListener("click", () => setVersePickerTab(tab.dataset.pickerTab));
  });
  document.getElementById("theme-search")?.addEventListener("input", debouncePickerSearch("openbible"));
  document.getElementById("naves-search")?.addEventListener("input", debouncePickerSearch("naves"));
  document.getElementById("theme-topic-list")?.addEventListener("click", (e) => onPickerTopicClick(e, "openbible"));
  document.getElementById("naves-topic-list")?.addEventListener("click", (e) => onPickerTopicClick(e, "naves"));
  document.getElementById("theme-verse-list")?.addEventListener("click", (e) => onPickerVerseListClick(e, "openbible"));
  document.getElementById("naves-verse-list")?.addEventListener("click", (e) => onPickerVerseListClick(e, "naves"));
  document.getElementById("book-list")?.addEventListener("click", onPickerBookClick);
  document.getElementById("book-chapter-list")?.addEventListener("click", onPickerChapterClick);
  document.getElementById("book-verse-form")?.addEventListener("submit", onPickerBookVerseSubmit);
}

function setVersePickerTab(tab) {
  if (!tab) return;
  versePickerState.activeTab = tab;
  document.querySelectorAll(".verse-picker-tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.pickerTab === tab);
  });
  document.querySelectorAll(".verse-picker-pane").forEach((pane) => {
    pane.hidden = pane.dataset.pickerPane !== tab;
  });
  if (tab === "theme" && !versePickerState.themeLoaded) loadPickerTopics("openbible");
  if (tab === "topic" && !versePickerState.navesLoaded) loadPickerTopics("naves");
  if (tab === "book" && !versePickerState.booksLoaded) loadPickerBooks();
}

let _pickerSearchTimers = {};
function debouncePickerSearch(source) {
  return (event) => {
    clearTimeout(_pickerSearchTimers[source]);
    const query = event.target.value;
    _pickerSearchTimers[source] = setTimeout(() => loadPickerTopics(source, query), 220);
  };
}

async function loadPickerTopics(source, query = "") {
  const listId = source === "openbible" ? "theme-topic-list" : "naves-topic-list";
  const verseListId = source === "openbible" ? "theme-verse-list" : "naves-verse-list";
  const list = document.getElementById(listId);
  const verseList = document.getElementById(verseListId);
  if (!list) return;
  verseList.hidden = true;
  verseList.innerHTML = "";
  list.hidden = false;
  list.innerHTML = '<p class="picker-empty-state">Loading...</p>';
  try {
    const params = new URLSearchParams({ source, limit: "75" });
    if (query.trim()) params.set("q", query.trim());
    const topics = await fetchJson(`/v1/topics?${params.toString()}`);
    if (source === "openbible") versePickerState.themeLoaded = true;
    else versePickerState.navesLoaded = true;
    if (!topics.length) {
      list.innerHTML = '<p class="picker-empty-state">No topics matched.</p>';
      return;
    }
    list.innerHTML = topics
      .map(
        (t) => `
        <button type="button" class="picker-list-item" data-topic-id="${escapeHtml(t.topic_id)}">
          <span>${escapeHtml(toTitleCase(t.name))}</span>
          <span class="picker-list-item-meta">${t.verse_count} verses</span>
        </button>`,
      )
      .join("");
  } catch (error) {
    list.innerHTML = `<p class="picker-empty-state">${escapeHtml(error.message || "Failed to load topics.")}</p>`;
  }
}

async function onPickerTopicClick(event, source) {
  const button = event.target.closest(".picker-list-item");
  if (!button) return;
  const topicId = button.dataset.topicId;
  const listId = source === "openbible" ? "theme-topic-list" : "naves-topic-list";
  const verseListId = source === "openbible" ? "theme-verse-list" : "naves-verse-list";
  const list = document.getElementById(listId);
  const verseList = document.getElementById(verseListId);
  list.hidden = true;
  verseList.hidden = false;
  verseList.innerHTML = '<p class="picker-empty-state">Loading verses...</p>';
  try {
    const data = await fetchJson(
      `/v1/topics/${encodeURIComponent(source)}/${encodeURIComponent(topicId)}/verses`,
    );
    const items = (data.verses || [])
      .map((v) => {
        const refLabel = formatReference(v);
        const payload = JSON.stringify(v).replaceAll('"', "&quot;");
        return `
          <button type="button" class="picker-list-item" data-verse-ref="${payload}">
            <span>${escapeHtml(refLabel)}</span>
            <span class="picker-list-item-meta">Add</span>
          </button>`;
      })
      .join("");
    verseList.innerHTML = `
      <button type="button" class="picker-back-button" data-picker-back>&larr; Back to topics</button>
      <p><strong>${escapeHtml(toTitleCase(data.name))}</strong></p>
      <div class="picker-list">${items || '<p class="picker-empty-state">No verses for this topic.</p>'}</div>
    `;
  } catch (error) {
    verseList.innerHTML = `<p class="picker-empty-state">${escapeHtml(error.message || "Failed to load verses.")}</p>`;
  }
}

async function onPickerVerseListClick(event, source) {
  if (event.target.closest("[data-picker-back]")) {
    const listId = source === "openbible" ? "theme-topic-list" : "naves-topic-list";
    const verseListId = source === "openbible" ? "theme-verse-list" : "naves-verse-list";
    document.getElementById(listId).hidden = false;
    document.getElementById(verseListId).hidden = true;
    document.getElementById(verseListId).innerHTML = "";
    return;
  }
  const button = event.target.closest("[data-verse-ref]");
  if (!button) return;
  const ref = JSON.parse(button.dataset.verseRef.replaceAll("&quot;", '"'));
  await addVerseFromReference(ref, button);
}

async function loadPickerBooks() {
  const list = document.getElementById("book-list");
  if (!list) return;
  list.innerHTML = '<p class="picker-empty-state">Loading books...</p>';
  try {
    const books = await fetchJson("/v1/books");
    versePickerState.booksLoaded = true;
    list.innerHTML = books
      .map(
        (b) => `
        <button type="button" class="picker-list-item" data-book-name="${escapeHtml(b.name)}" data-chapters="${b.chapters}">
          <span>${escapeHtml(b.name)}</span>
          <span class="picker-list-item-meta">${b.chapters} ch &middot; ${b.testament === "old" ? "OT" : "NT"}</span>
        </button>`,
      )
      .join("");
  } catch (error) {
    list.innerHTML = `<p class="picker-empty-state">${escapeHtml(error.message || "Failed to load books.")}</p>`;
  }
}

function onPickerBookClick(event) {
  const button = event.target.closest("[data-book-name]");
  if (!button) return;
  const book = button.dataset.bookName;
  const chapters = Number(button.dataset.chapters) || 1;
  versePickerState.selectedBook = book;
  versePickerState.selectedChapter = null;
  const bookList = document.getElementById("book-list");
  const chapterList = document.getElementById("book-chapter-list");
  const form = document.getElementById("book-verse-form");
  bookList.hidden = true;
  chapterList.hidden = false;
  form.hidden = true;
  const chips = [];
  for (let i = 1; i <= chapters; i += 1) {
    chips.push(
      `<button type="button" class="picker-list-item" data-chapter="${i}"><span>Chapter ${i}</span></button>`,
    );
  }
  chapterList.innerHTML = `
    <button type="button" class="picker-back-button" data-picker-back-book>&larr; Back to books</button>
    <p><strong>${escapeHtml(book)}</strong></p>
    ${chips.join("")}
  `;
}

function onPickerChapterClick(event) {
  if (event.target.closest("[data-picker-back-book]")) {
    document.getElementById("book-list").hidden = false;
    document.getElementById("book-chapter-list").hidden = true;
    document.getElementById("book-verse-form").hidden = true;
    versePickerState.selectedBook = null;
    return;
  }
  const button = event.target.closest("[data-chapter]");
  if (!button) return;
  const chapter = Number(button.dataset.chapter);
  versePickerState.selectedChapter = chapter;
  const form = document.getElementById("book-verse-form");
  form.hidden = false;
  document.getElementById("book-verse-summary").textContent =
    `${versePickerState.selectedBook} ${chapter}:?`;
  document.getElementById("book-start-verse").value = "";
  document.getElementById("book-end-verse").value = "";
  document.getElementById("book-start-verse").focus();
}

async function onPickerBookVerseSubmit(event) {
  event.preventDefault();
  const start = optionalNumber(document.getElementById("book-start-verse").value);
  const end = optionalNumber(document.getElementById("book-end-verse").value);
  if (!versePickerState.selectedBook || !versePickerState.selectedChapter || !start) {
    showToast("Pick a book, chapter, and start verse.");
    return;
  }
  await addVerseFromReference(
    {
      book: versePickerState.selectedBook,
      chapter: versePickerState.selectedChapter,
      start_verse: start,
      end_verse: end,
    },
    event.submitter,
  );
}

async function addVerseFromReference(reference, button) {
  if (!ensureLiveMode("Demo mode is read-only. Switch to Live to add verses.")) return;
  const userId = getUserId();
  if (button) {
    button.disabled = true;
  }
  try {
    await fetchJson("/v1/memorization/verses", {
      method: "POST",
      body: {
        user_id: userId,
        book: reference.book,
        chapter: reference.chapter,
        start_verse: reference.start_verse,
        end_verse: reference.end_verse ?? null,
      },
    });
    showToast(`Added ${formatReference(reference)} from ESV.`);
    await loadMemorizeScreen();
  } catch (error) {
    handleError(error);
  } finally {
    if (button) {
      button.disabled = false;
    }
  }
}

function toTitleCase(text) {
  if (!text) return "";
  return text.replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
}

async function loadMemorizeScreen() {
  const userId = getUserId();
  const [verses, progress] = await Promise.all([
    fetchJson(`/v1/memorization/${encodeURIComponent(userId)}/verses`),
    fetchJson(`/v1/memorization/${encodeURIComponent(userId)}/progress`),
  ]);
  memorizeState.verses = Array.isArray(verses) ? verses : [];
  memorizeState.progress = progress;
  renderMemorizeProgress();
  renderMemorizeTarget();
  renderMemorizeVerseList();
}

function renderMemorizeProgress() {
  const progress = memorizeState.progress;
  const due = progress?.due_today || 0;
  const total = progress?.total_verses || 0;
  const mastery = progress?.mastery || { learning: 0, familiar: 0, mastered: 0 };
  const streak = progress?.current_streak || 0;
  setTextById("memorize-streak-pill", `${streak} day streak`);
  setTextById("memorize-due-value", String(due));
  setTextById(
    "memorize-due-copy",
    due === 0
      ? total === 0
        ? "Nothing due. Add a verse to get started."
        : "All caught up. New reviews unlock as intervals come due."
      : `${due} verse${due === 1 ? "" : "s"} ready for review.`,
  );
  setTextById("memorize-mastery-value", `${total} verse${total === 1 ? "" : "s"}`);
  setTextById(
    "memorize-mastery-copy",
    `Learning ${mastery.learning} · Familiar ${mastery.familiar} · Mastered ${mastery.mastered}`,
  );
  const startButton = document.getElementById("memorize-start-review-button");
  if (startButton) {
    startButton.disabled = due === 0;
    startButton.textContent = due === 0 ? "Nothing due to review" : `Start today's review (${due})`;
  }
}

function renderMemorizeTarget() {
  const target = memorizeState.progress?.active_target;
  const progress = memorizeState.progress?.active_target_progress || 0;
  const pill = document.getElementById("memorize-target-pill");
  const card = document.getElementById("memorize-target-card");
  if (!card) return;
  if (!target) {
    if (pill) pill.textContent = "No target";
    card.innerHTML = '<p class="empty-state">Set a target below to keep momentum visible.</p>';
    return;
  }
  const goal = target.verse_count_goal;
  const percent = goal > 0 ? Math.min(100, Math.round((progress / goal) * 100)) : 0;
  if (pill) pill.textContent = target.status === "achieved" ? "Achieved" : `${percent}%`;
  card.innerHTML = `
    <div class="inline-card">
      <p><strong>${escapeHtml(target.title)}</strong></p>
      <p class="micro-copy">By ${escapeHtml(target.target_date)} · ${progress} / ${goal} verses familiar or mastered</p>
      <div class="progress-bar"><div class="progress-bar-fill" style="width:${percent}%"></div></div>
    </div>
  `;
}

function renderMemorizeVerseList() {
  const list = document.getElementById("memorize-verse-list");
  if (!list) return;
  if (!memorizeState.verses.length) {
    list.innerHTML = '<p class="empty-state">No verses yet. Add one above to begin.</p>';
    return;
  }
  list.innerHTML = memorizeState.verses
    .map((verse) => {
      const reference = formatReference(verse.reference);
      const mastery = verse.mastery_level || "learning";
      const preview = (verse.verse_text || "").replace(/<[^>]+>/g, "").slice(0, 160);
      const reviewLabel = mastery === "mastered"
        ? `Reminder ${formatReviewDate(verse.next_review_at)}`
        : `Next review ${formatReviewDate(verse.next_review_at)}`;
      return `
        <article class="inline-card">
          <p><strong>${escapeHtml(reference)}</strong> <span class="mastery-chip mastery-${escapeHtml(mastery)}">${escapeHtml(sentenceCase(mastery))}</span></p>
          <p class="micro-copy">${escapeHtml(reviewLabel)} · ${verse.repetition_count} reps</p>
          <p>${escapeHtml(preview)}${preview.length === 160 ? "…" : ""}</p>
          <div class="source-card-actions">
            <button type="button" class="secondary-button" data-action="drill" data-verse-id="${escapeHtml(verse.verse_id)}">${mastery === "mastered" ? "Review" : "Drill"}</button>
            <button type="button" class="secondary-button" data-action="delete" data-verse-id="${escapeHtml(verse.verse_id)}">Remove</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function formatReviewDate(value) {
  if (!value) return "today";
  const target = new Date(`${value}T00:00:00`);
  if (Number.isNaN(target.getTime())) return value;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffDays = Math.round((target - today) / 86400000);
  if (diffDays < 0) return `overdue (${Math.abs(diffDays)}d)`;
  if (diffDays === 0) return "today";
  if (diffDays === 1) return "tomorrow";
  if (diffDays <= 7) return `in ${diffDays} days`;
  return `on ${target.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`;
}

async function onAddMemorizedVerse(event) {
  event.preventDefault();
  if (!ensureLiveMode("Demo mode is read-only. Switch to Live to add verses.")) return;
  const userId = getUserId();
  const book = optionalText(document.getElementById("memorize-add-book").value);
  const chapter = optionalNumber(document.getElementById("memorize-add-chapter").value);
  const startVerse = optionalNumber(document.getElementById("memorize-add-start").value);
  const endVerse = optionalNumber(document.getElementById("memorize-add-end").value);
  if (!book || !chapter || !startVerse) {
    showToast("Add a book, chapter, and start verse first.");
    return;
  }
  try {
    await fetchJson("/v1/memorization/verses", {
      method: "POST",
      body: {
        user_id: userId,
        book,
        chapter,
        start_verse: startVerse,
        end_verse: endVerse,
      },
    });
    showToast(`Added ${book} ${chapter}:${startVerse} from ESV.`);
    event.target.reset();
    await loadMemorizeScreen();
  } catch (error) {
    handleError(error);
  }
}

async function onCreateMemorizationTarget(event) {
  event.preventDefault();
  if (!ensureLiveMode("Demo mode is read-only.")) return;
  const userId = getUserId();
  const title = optionalText(document.getElementById("memorize-target-title").value);
  const count = optionalNumber(document.getElementById("memorize-target-count").value);
  const date = optionalText(document.getElementById("memorize-target-date").value);
  if (!title || !count || !date) {
    showToast("Add a title, verse count, and target date.");
    return;
  }
  try {
    await fetchJson(`/v1/memorization/${encodeURIComponent(userId)}/targets`, {
      method: "POST",
      body: { title, verse_count_goal: count, target_date: date },
    });
    showToast("Memorization target saved.");
    event.target.reset();
    await loadMemorizeScreen();
  } catch (error) {
    handleError(error);
  }
}

async function onMemorizeVerseListClick(event) {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const verseId = button.dataset.verseId;
  const verse = memorizeState.verses.find((item) => item.verse_id === verseId);
  if (!verse) return;
  if (button.dataset.action === "drill") {
    startMemorizationDrill([verse]);
  } else if (button.dataset.action === "delete") {
    if (!confirm(`Remove ${formatReference(verse.reference)} from memorization?`)) return;
    try {
      await fetchJson(`/v1/memorization/verses/${encodeURIComponent(verseId)}`, { method: "DELETE" });
      showToast("Verse removed.");
      await loadMemorizeScreen();
    } catch (error) {
      handleError(error);
    }
  }
}

async function onStartMemorizationReview() {
  const userId = getUserId();
  try {
    const queue = await fetchJson(`/v1/memorization/${encodeURIComponent(userId)}/queue`);
    if (!Array.isArray(queue) || queue.length === 0) {
      showToast("Nothing due to review right now.");
      return;
    }
    startMemorizationDrill(queue);
  } catch (error) {
    handleError(error);
  }
}

function startMemorizationDrill(verses) {
  memorizeState.drill = { queue: [...verses], index: 0 };
  const panel = document.getElementById("memorize-drill-panel");
  if (panel) panel.hidden = false;
  renderMemorizeDrillStage();
  panel?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function exitMemorizationDrill() {
  memorizeState.drill = null;
  const panel = document.getElementById("memorize-drill-panel");
  if (panel) panel.hidden = true;
}

function renderMemorizeDrillStage() {
  const drill = memorizeState.drill;
  if (!drill) return;
  const verse = drill.queue[drill.index];
  if (!verse) {
    exitMemorizationDrill();
    showToast("You finished the review queue.");
    loadMemorizeScreen().catch(handleError);
    return;
  }
  const isMastered = verse.mastery_level === "mastered";
  const stage = isMastered
    ? MEMORIZE_DRILL_STAGES.length - 1
    : Math.min(verse.learning_stage || 0, MEMORIZE_DRILL_STAGES.length - 1);
  const stageMeta = MEMORIZE_DRILL_STAGES[stage];
  setTextById("memorize-drill-reference", formatReference(verse.reference));
  setTextById(
    "memorize-drill-progress-pill",
    `${drill.index + 1} / ${drill.queue.length}`,
  );
  setTextById(
    "memorize-drill-stage-copy",
    isMastered
      ? `Mastered review — ${stageMeta.label}`
      : `Stage ${stage + 1} of ${MEMORIZE_DRILL_STAGES.length} — ${stageMeta.label}`,
  );
  const display = document.getElementById("memorize-drill-display");
  if (display) display.innerHTML = renderDrillVerseHtml(verse.verse_text, stage);

  const learningSection = document.getElementById("memorize-drill-learning");
  const reviewSection = document.getElementById("memorize-drill-review");
  if (learningSection) learningSection.hidden = isMastered;
  if (reviewSection) reviewSection.hidden = !isMastered;

  const input = document.getElementById("memorize-drill-input");
  if (input) input.value = "";
  const resultEl = document.getElementById("memorize-drill-result");
  if (resultEl) {
    resultEl.hidden = true;
    resultEl.innerHTML = "";
  }
}

function renderDrillVerseHtml(verseText, stage) {
  const cleaned = (verseText || "").replace(/\s+/g, " ").trim();
  if (!cleaned) return "<em>This verse has no text.</em>";
  if (stage === 0) return escapeHtml(cleaned);
  const tokens = cleaned.split(/(\s+)/);
  let wordIndex = -1;
  const transformed = tokens.map((token) => {
    if (/^\s+$/.test(token) || !/[A-Za-z]/.test(token)) return token;
    wordIndex += 1;
    return transformWord(token, stage, wordIndex);
  });
  return escapeHtml(transformed.join(""));
}

function transformWord(word, stage, wordIndex) {
  const letters = word.match(/[A-Za-z]+/);
  if (!letters) return word;
  const lettersStr = letters[0];
  const firstLetter = lettersStr.charAt(0);
  if (stage === 1) {
    return wordIndex % 3 === 2
      ? word.replace(/[A-Za-z]+/, (group) => "_".repeat(Math.max(group.length, 3)))
      : word;
  }
  if (stage === 2) {
    return word.replace(/[A-Za-z]+/, (group) => group.charAt(0) + "_".repeat(Math.max(group.length - 1, 1)));
  }
  if (stage === 3) {
    return word.replace(/[A-Za-z]+/, firstLetter);
  }
  if (stage === 4) {
    return wordIndex === 0
      ? word
      : word.replace(/[A-Za-z]+/, (group) => "_".repeat(Math.max(group.length, 3)));
  }
  return word;
}

async function onMemorizeDrillSubmit() {
  const drill = memorizeState.drill;
  if (!drill) return;
  const verse = drill.queue[drill.index];
  if (!verse) return;
  const input = document.getElementById("memorize-drill-input");
  const typedText = (input?.value || "").trim();
  if (!typedText) {
    showToast("Type the verse from memory first.");
    return;
  }
  try {
    const payload = await fetchJson(
      `/v1/memorization/verses/${encodeURIComponent(verse.verse_id)}/drill-attempt`,
      { method: "POST", body: { typed_text: typedText } },
    );
    const result = payload.result;
    drill.queue[drill.index] = result.verse;
    const versesIndex = memorizeState.verses.findIndex((v) => v.verse_id === result.verse.verse_id);
    if (versesIndex >= 0) memorizeState.verses[versesIndex] = result.verse;
    if (payload.progress) {
      memorizeState.progress = payload.progress;
      renderMemorizeProgress();
      renderMemorizeTarget();
    }
    renderDrillAttemptResult(result);
  } catch (error) {
    handleError(error);
  }
}

function renderDrillAttemptResult(result) {
  const resultEl = document.getElementById("memorize-drill-result");
  const display = document.getElementById("memorize-drill-display");
  const input = document.getElementById("memorize-drill-input");
  const verse = result.verse;
  const isMastered = verse.mastery_level === "mastered";
  const newStage = isMastered
    ? MEMORIZE_DRILL_STAGES.length - 1
    : Math.min(verse.learning_stage || 0, MEMORIZE_DRILL_STAGES.length - 1);

  if (display) display.innerHTML = renderDrillVerseHtml(verse.verse_text, newStage);
  if (input) input.value = "";
  setTextById(
    "memorize-drill-stage-copy",
    isMastered
      ? `Mastered — review with rating buttons below.`
      : `Stage ${newStage + 1} of ${MEMORIZE_DRILL_STAGES.length} — ${MEMORIZE_DRILL_STAGES[newStage].label}`,
  );

  const learningSection = document.getElementById("memorize-drill-learning");
  const reviewSection = document.getElementById("memorize-drill-review");
  if (learningSection) learningSection.hidden = isMastered;
  if (reviewSection) reviewSection.hidden = !isMastered;

  if (!resultEl) return;
  const percent = Math.round(result.score * 100);
  let outcomeClass = "drill-result-stay";
  let outcomeMsg;
  if (result.mastered) {
    outcomeClass = "drill-result-mastered";
    const reminder = formatReviewDate(verse.next_review_at);
    outcomeMsg = `Mastered! Reminder set ${reminder}. Pick another verse to keep going.`;
  } else if (result.advanced) {
    outcomeClass = "drill-result-advance";
    outcomeMsg = `Nice — advancing to stage ${newStage + 1} of ${MEMORIZE_DRILL_STAGES.length}.`;
  } else {
    outcomeMsg = "Try again — get to 90% to advance.";
  }
  const diffHtml = result.diff
    .map((entry) => {
      if (entry.ok) return `<span class="word-diff ok">${escapeHtml(entry.expected)}</span>`;
      const expected = entry.expected ? escapeHtml(entry.expected) : "—";
      const typed = entry.typed ? escapeHtml(entry.typed) : "—";
      return `<span class="word-diff miss" title="You typed: ${typed}">${expected}</span>`;
    })
    .join(" ");
  const masteredActions = result.mastered
    ? `<div class="source-card-actions">
        <button type="button" class="primary-button" id="drill-pick-next-verse">Pick another verse</button>
        <button type="button" class="secondary-button" id="drill-finish">Finish drill</button>
      </div>`
    : "";
  resultEl.innerHTML = `
    <div class="${outcomeClass}">
      <p><strong>${percent}%</strong> — ${result.correct_words} / ${result.total_words} words correct</p>
      <p>${escapeHtml(outcomeMsg)}</p>
      <div class="word-diff-row">${diffHtml}</div>
      ${masteredActions}
    </div>
  `;
  resultEl.hidden = false;
  if (result.mastered) {
    document.getElementById("drill-pick-next-verse")?.addEventListener("click", () => {
      exitMemorizationDrill();
      const addForm = document.getElementById("memorize-add-verse-form");
      addForm?.scrollIntoView({ behavior: "smooth", block: "center" });
      document.getElementById("memorize-add-book")?.focus();
    });
    document.getElementById("drill-finish")?.addEventListener("click", () => {
      exitMemorizationDrill();
      loadMemorizeScreen().catch(handleError);
    });
  }
}

async function onMemorizeRatingClick(event) {
  const button = event.target.closest("button[data-rating]");
  if (!button) return;
  const drill = memorizeState.drill;
  if (!drill) return;
  const verse = drill.queue[drill.index];
  if (!verse) return;
  const rating = button.dataset.rating;
  try {
    await fetchJson(`/v1/memorization/verses/${encodeURIComponent(verse.verse_id)}/review`, {
      method: "POST",
      body: { rating, drill_stage: MEMORIZE_DRILL_STAGES.length - 1 },
    });
    showToast(`Saved as "${rating}".`);
    drill.index += 1;
    renderMemorizeDrillStage();
  } catch (error) {
    handleError(error);
  }
}

function bindStudyNotesEvents() {
  document.getElementById("study-notes-form")?.addEventListener("submit", onSaveStudyNote);
  document.getElementById("study-notes-list")?.addEventListener("click", onStudyNotesListClick);
}

function activeStudyReference() {
  return state.activeSessionPayload?.session?.reference || null;
}

async function refreshStudyNotes() {
  const userId = getUserId();
  const reference = activeStudyReference();
  notesState.reference = reference;
  const submitButton = document.getElementById("study-notes-submit");
  const referenceCopy = document.getElementById("study-notes-reference-copy");
  const pill = document.getElementById("study-notes-pill");
  const list = document.getElementById("study-notes-list");
  if (!list || !submitButton || !referenceCopy || !pill) return;
  if (!reference) {
    notesState.notes = [];
    submitButton.disabled = true;
    referenceCopy.textContent = "Start a session to capture notes on the active passage.";
    pill.textContent = "0 notes";
    list.innerHTML = '<p class="empty-state">Notes will appear once you start a session.</p>';
    return;
  }
  submitButton.disabled = false;
  referenceCopy.textContent = `Notes on ${formatReference(reference)}.`;
  try {
    const params = new URLSearchParams({
      book: reference.book,
      chapter: String(reference.chapter),
      start_verse: String(reference.start_verse),
    });
    if (reference.end_verse) params.set("end_verse", String(reference.end_verse));
    const notes = await fetchJson(`/v1/notes/${encodeURIComponent(userId)}?${params.toString()}`);
    notesState.notes = Array.isArray(notes) ? notes : [];
    pill.textContent = `${notesState.notes.length} note${notesState.notes.length === 1 ? "" : "s"}`;
    if (!notesState.notes.length) {
      list.innerHTML = '<p class="empty-state">No notes on this passage yet.</p>';
      return;
    }
    list.innerHTML = notesState.notes
      .map(
        (note) => `
        <article class="inline-card">
          ${note.title ? `<p><strong>${escapeHtml(note.title)}</strong></p>` : ""}
          <p>${escapeHtml(note.body).replace(/\n/g, "<br>")}</p>
          <p class="micro-copy">Saved ${escapeHtml((note.updated_at || note.created_at || "").slice(0, 10))}</p>
          <div class="source-card-actions">
            <button type="button" class="secondary-button" data-action="delete-note" data-note-id="${escapeHtml(note.note_id)}">Delete</button>
          </div>
        </article>
      `,
      )
      .join("");
  } catch (error) {
    handleError(error);
  }
}

async function onSaveStudyNote(event) {
  event.preventDefault();
  if (!ensureLiveMode("Demo mode is read-only. Switch to Live to save notes.")) return;
  const reference = activeStudyReference();
  if (!reference) {
    showToast("Start a session before saving notes.");
    return;
  }
  const title = optionalText(document.getElementById("study-notes-title").value);
  const body = optionalText(document.getElementById("study-notes-body").value);
  if (!body) {
    showToast("Add a note before saving.");
    return;
  }
  try {
    await fetchJson("/v1/notes", {
      method: "POST",
      body: {
        user_id: getUserId(),
        book: reference.book,
        chapter: reference.chapter,
        start_verse: reference.start_verse,
        end_verse: reference.end_verse || null,
        title,
        body,
        session_id: state.activeSessionPayload?.session?.session_id || null,
      },
    });
    showToast("Note saved.");
    document.getElementById("study-notes-title").value = "";
    document.getElementById("study-notes-body").value = "";
    await refreshStudyNotes();
  } catch (error) {
    handleError(error);
  }
}

async function onStudyNotesListClick(event) {
  const button = event.target.closest("button[data-action='delete-note']");
  if (!button) return;
  const noteId = button.dataset.noteId;
  if (!noteId) return;
  if (!confirm("Delete this note?")) return;
  try {
    await fetchJson(`/v1/notes/${encodeURIComponent(noteId)}`, { method: "DELETE" });
    showToast("Note deleted.");
    await refreshStudyNotes();
  } catch (error) {
    handleError(error);
  }
}

function setTextById(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function showToast(message) {
  window.clearTimeout(state.toastTimer);
  elements.toast.textContent = message;
  elements.toast.classList.add("toast-visible");
  state.toastTimer = window.setTimeout(() => {
    elements.toast.classList.remove("toast-visible");
  }, 2800);
}

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

function sentenceCase(value) {
  if (!value) {
    return "";
  }
  const normalized = String(value).replaceAll("_", " ");
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}


function humanizeGuideMode(value) {
  const labels = {
    guide: "Guided study",
    peer: "Conversation guide",
    challenger: "Deeper challenge",
    coach: "Coaching guide",
  };
  return labels[value] || sentenceCase(value);
}

function humanizeFocusArea(value) {
  const labels = {
    comprehension: "Understanding the passage",
    application: "Living it out",
    consistency: "Steady rhythm",
    growth: "Deeper growth",
  };
  return labels[value] || sentenceCase(value);
}

function humanizeQuestionType(value) {
  const labels = {
    observation: "Notice what stands out",
    interpretation: "Understand the meaning",
    application: "Live it out",
    reflection: "Reflect honestly",
  };
  return labels[value] || sentenceCase(value);
}

function humanizeEntryPoint(value) {
  const labels = {
    "continue where I left off": "Pick up where I left off",
    "I need clarity before application": "Help me understand before I apply this",
    "I want to begin gently": "Ease me in gently",
  };
  const resolved = labels[value] || polishGuideCopy(value || "");
  return tidyGuidanceLine(resolved);
}

function tidyGuidanceLine(value) {
  const normalized = String(value || "").trim().replace(/\s+/g, " ");
  if (!normalized) {
    return "";
  }
  return normalized.replace(/[\u2026]+$/g, "").replace(/[.]{3,}$/g, "").trim();
}

function humanizeNudgeType(value) {
  const labels = {
    momentum: "Momentum",
    restart: "Restart",
    follow_through: "Follow-through",
    encouragement: "Encouragement",
    theme: "Carry-forward",
  };
  return labels[value] || sentenceCase(value);
}

function setupModeLabel(value) {
  const labels = {
    starter: "Starter",
    esv_api: "ESV connection",
    upload: "Upload",
    generic_api: "Provider connection",
  };
  return labels[value] || sentenceCase(value);
}

function polishGuideCopy(value) {
  if (!value) {
    return "";
  }
  return String(value)
    .replaceAll("A gentle restart will help rebuild rhythm without overwhelming the user.", "A gentle restart can help you rebuild a steady rhythm without feeling overwhelmed.")
    .replaceAll("The user is still building an initial study rhythm.", "You're still building a steady study rhythm.")
    .replaceAll("The user is still building a study rhythm.", "You're still building a study rhythm.")
    .replaceAll("The user ", "You ")
    .replaceAll(" the user ", " you ");
}
function formatReference(reference) {
  if (!reference) {
    return "Unknown reference";
  }
  const endVerse = reference.end_verse ? `-${reference.end_verse}` : "";
  return `${reference.book} ${reference.chapter}:${reference.start_verse}${endVerse}`;
}

function truncateGuideCopy(value, maxLength = 150) {
  if (!value) {
    return "";
  }
  const trimmed = String(value).trim();
  if (trimmed.length <= maxLength) {
    return trimmed;
  }
  const shortened = trimmed.slice(0, Math.max(0, maxLength - 1));
  const lastSpace = shortened.lastIndexOf(" ");
  const safeCut = lastSpace > 60 ? shortened.slice(0, lastSpace) : shortened;
  return `${safeCut}...`;
}

function formatDateTime(value, timezone = undefined) {
  if (!value) {
    return "";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
    ...(timezone ? { timeZone: timezone } : {}),
  }).format(parsed);
}

function formatDateOnly(value) {
  if (!value) {
    return "";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(parsed);
}

function buildQuestionProgress(session) {
  const total = safeArray(session?.questions).length;
  if (!total) {
    return "Questions unavailable";
  }
  const current = Math.min(session.current_question_index + 1, total);
  return `Question ${current} of ${total}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
async function loadTextSources() {
  if (isDemoMode()) {
    state.textSources = DEFAULT_TEXT_SOURCES;
    renderTextSourceOptions();
    return;
  }
  try {
    const response = await fetchJson("/v1/sources/text");
    state.textSources = response.items || response.sources || response || [];
  } catch {
    state.textSources = DEFAULT_TEXT_SOURCES;
  }
  renderTextSourceOptions();
}



function bibleSourceElements() {
  return {
    templateList: document.getElementById("translation-template-list"),
    library: document.getElementById("source-library"),
    copy: document.getElementById("source-manager-copy"),
    useStarterButton: document.getElementById("source-use-starter"),
    focusEsvButton: document.getElementById("source-focus-esv"),
    esvForm: document.getElementById("source-esv-form"),
    esvKey: document.getElementById("source-esv-key"),
    advancedToggle: document.getElementById("source-advanced-toggle"),
    advancedPanel: document.getElementById("source-advanced-panel"),
    setupOptions: document.getElementById("source-setup-options"),
    uploadForm: document.getElementById("source-upload-form"),
    uploadName: document.getElementById("source-upload-name"),
    uploadFile: document.getElementById("source-upload-file"),
    apiForm: document.getElementById("source-api-form"),
    apiName: document.getElementById("source-api-name"),
    apiUrl: document.getElementById("source-api-url"),
    apiKey: document.getElementById("source-api-key"),
    currentName: document.getElementById("source-current-name"),
    currentDetail: document.getElementById("source-current-detail"),
    manageToggle: document.getElementById("source-manage-toggle"),
    details: document.getElementById("source-manager-details"),
  };
}

document.addEventListener("DOMContentLoaded", () => {
  const sourceUi = bibleSourceElements();
  sourceUi.templateList?.addEventListener("click", reportFailures(onTranslationTemplateClick));
  sourceUi.library?.addEventListener("click", reportFailures(onSourceLibraryClick));
  sourceUi.useStarterButton?.addEventListener("click", reportFailures(onUseStarterBible));
  sourceUi.focusEsvButton?.addEventListener("click", reportFailures(onPrimaryEsvAction));
  sourceUi.esvForm?.addEventListener("submit", reportFailures(onConnectEsvSource));
  sourceUi.advancedToggle?.addEventListener("click", onToggleAdvancedBibleSetup);
  sourceUi.uploadForm?.addEventListener("submit", reportFailures(onUploadBibleSource));
  sourceUi.apiForm?.addEventListener("submit", reportFailures(onConnectBibleApiSource));
});

function renderBibleSourceManager() {
  const sourceUi = bibleSourceElements();
  if (!sourceUi.library || !sourceUi.copy) {
    return;
  }

  const sources = (state.textSources.length ? state.textSources : DEFAULT_TEXT_SOURCES).filter(
    (source) => source.source_id !== "user_api_placeholder",
  );
  const preferredSourceId = getEffectivePreferredSourceId(sources);
  const preferredSource = sources.find((source) => source.source_id === preferredSourceId) || null;
  const starterSource = sources.find((source) => source.source_id === STARTER_SOURCE_ID) || null;
  const esvSource = sources.find((source) => source.source_id === ESV_SOURCE_ID) || null;
  const currentProviderLabel = !preferredSource
    ? "Choose the Bible Emmaus should use for new sessions."
    : preferredSource.source_id === ESV_SOURCE_ID || preferredSource.metadata?.vendor === "esv"
      ? "Official ESV API connection"
      : preferredSource.provider_type === "remote_api"
        ? "Connected provider"
        : preferredSource.source_id === STARTER_SOURCE_ID
          ? "Included with Emmaus"
          : "Uploaded from this device";

  sourceUi.copy.textContent = preferredSource
    ? `Emmaus will use ${preferredSource.name} for new sessions. You can change it any time.`
    : "Choose a Bible and Emmaus will use it for new sessions.";

  if (sourceUi.currentName) {
    sourceUi.currentName.textContent = preferredSource?.name || "Choose your Bible";
  }
    if (elements.homeBibleCurrentName) {
      elements.homeBibleCurrentName.textContent = preferredSource?.name || "Choose your Bible";
    }
  if (sourceUi.currentDetail) {
    sourceUi.currentDetail.textContent = preferredSource
      ? `${preferredSource.name} is your current Bible for new sessions. Active sessions keep the Bible they started with.`
      : currentProviderLabel;
  }

  const shouldExpand = state.bibleManagerExpanded || !preferredSourceId;
  setBibleManagerExpanded(shouldExpand);
  setBibleSetupExpanded(shouldExpand && state.bibleSetupExpanded);

  renderTranslationTemplates(sources, preferredSourceId);
  renderSourcePreview(state.sourcePreview);

  if (sourceUi.useStarterButton) {
    const starterActive = preferredSourceId === STARTER_SOURCE_ID;
    sourceUi.useStarterButton.disabled = !starterSource || starterActive;
    sourceUi.useStarterButton.textContent = starterActive ? "Using included starter Bible" : "Use included starter Bible";
  }

  if (sourceUi.focusEsvButton) {
    const esvActive = preferredSourceId === ESV_SOURCE_ID;
    sourceUi.focusEsvButton.disabled = Boolean(esvSource && esvActive);
    sourceUi.focusEsvButton.textContent = esvSource
      ? (esvActive ? "Using connected ESV" : "Use connected ESV")
      : "Connect ESV";
  }

  const connectedSources = sources.filter((source) => source.source_id !== STARTER_SOURCE_ID);
  if (!connectedSources.length) {
    sourceUi.library.innerHTML = '<p class="empty-state">No other Bibles are connected yet. You can start with the included Bible or upload one from this device.</p>';
    return;
  }

  sourceUi.library.innerHTML = connectedSources
    .map((source) => {
      const isPreferred = source.source_id === preferredSourceId;
      const providerLabel = source.source_id === ESV_SOURCE_ID || source.metadata?.vendor === "esv"
        ? "Official ESV API connection"
        : source.provider_type === "remote_api"
          ? "Connected provider"
          : "Uploaded from this device";
      return `
        <article class="action-card ${isPreferred ? "selected" : ""}">
          <div class="action-card-header">
            <div>
              <p><strong>${escapeHtml(source.name)}</strong></p>
              <p>${escapeHtml(providerLabel)}</p>
            </div>
            <span class="status-pill">${isPreferred ? "Current" : "Ready"}</span>
          </div>
          <div class="source-card-actions dual-actions">
            <button class="action-button" type="button" data-source-prefer="${escapeHtml(source.source_id)}" ${isPreferred ? "disabled" : ""}>${isPreferred ? "Using this Bible" : "Use this Bible"}</button>
            <button class="action-button" type="button" data-source-preview="${escapeHtml(source.source_id)}">Preview sample</button>
          </div>
        </article>
      `;
    })
    .join("");
}

async function onTranslationTemplateClick(event) {
  const previewButton = event.target.closest("[data-template-preview-source]");
  if (previewButton) {
    await previewBibleSource(previewButton.dataset.templatePreviewSource);
    return;
  }

  const button = event.target.closest("[data-template-action]");
  if (!button) {
    return;
  }

  const action = button.dataset.templateAction;
  const translationName = button.dataset.templateName || "this Bible";
  if (action === "starter") {
    await onUseStarterBible();
    return;
  }
  if (action === "esv_api") {
    await onPrimaryEsvAction();
    return;
  }

  if (!state.bibleManagerExpanded) {
    setBibleManagerExpanded(true);
  }

  const sourceUi = bibleSourceElements();
  if (action === "upload") {
    if (sourceUi.uploadName && !sourceUi.uploadName.value) {
      sourceUi.uploadName.value = translationName;
    }
    sourceUi.uploadForm?.scrollIntoView({ behavior: "smooth", block: "center" });
    sourceUi.uploadFile?.focus();
    showToast(`Add a ${translationName} JSON file to finish setup.`);
    return;
  }

  if (sourceUi.apiName && !sourceUi.apiName.value) {
    sourceUi.apiName.value = translationName;
  }
  if (!state.bibleSetupExpanded) {
    onToggleAdvancedBibleSetup();
  }
  sourceUi.apiForm?.scrollIntoView({ behavior: "smooth", block: "center" });
  sourceUi.apiUrl?.focus();
  showToast(`Connect your ${translationName} provider to use it in Emmaus.`);
}

async function onSourceLibraryClick(event) {
  const previewButton = event.target.closest("[data-source-preview]");
  if (previewButton) {
    await previewBibleSource(previewButton.dataset.sourcePreview);
    return;
  }

  const button = event.target.closest("[data-source-prefer]");
  if (!button) {
    return;
  }
  await setPreferredBibleSource(button.dataset.sourcePrefer);
}

async function onUseStarterBible() {
  await setPreferredBibleSource(STARTER_SOURCE_ID, { successMessage: "The included starter Bible is now your default." });
}

function onFocusEsvSource() {
  if (!state.bibleManagerExpanded) {
    setBibleManagerExpanded(true);
  }
  if (!state.bibleSetupExpanded) {
    setBibleSetupExpanded(true);
  }
  const sourceUi = bibleSourceElements();
  sourceUi.esvForm?.scrollIntoView({ behavior: "smooth", block: "center" });
  sourceUi.esvKey?.focus();
}

async function onPrimaryEsvAction() {
  const esvSource = getSourceById(ESV_SOURCE_ID);
  if (esvSource) {
    await setPreferredBibleSource(ESV_SOURCE_ID, { successMessage: "ESV is now your default Bible." });
    return;
  }
  onFocusEsvSource();
}

function onToggleAdvancedBibleSetup() {
  if (!state.bibleManagerExpanded) {
    setBibleManagerExpanded(true);
  }
  setBibleSetupExpanded(!state.bibleSetupExpanded);
}

async function onConnectEsvSource(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to connect a real Bible source.")) {
    return;
  }

  const sourceUi = bibleSourceElements();
  const apiKey = optionalText(sourceUi.esvKey?.value);
  if (!apiKey) {
    showToast("Paste your ESV API key first.");
    return;
  }

  const descriptor = await fetchJson("/v1/sources/text/esv", {
    method: "POST",
    body: {
      api_key: apiKey,
      source_id: ESV_SOURCE_ID,
      name: "ESV",
    },
  });

  setStoredOnboardingStep(2);
  await setPreferredBibleSource(descriptor.source_id, { successMessage: "ESV is now your default Bible." });
  sourceUi.esvForm?.reset();
}

async function onUploadBibleSource(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to connect a real Bible source.")) {
    return;
  }

  const sourceUi = bibleSourceElements();
  const file = sourceUi.uploadFile?.files?.[0];
  if (!file) {
    showToast("Choose a Bible JSON file first.");
    return;
  }

  const sourceName = optionalText(sourceUi.uploadName.value) || file.name.replace(/\.json$/i, "");
  const sourceId = buildGeneratedSourceId(sourceName);
  const fileContent = await file.text();

  const descriptor = await fetchJson("/v1/sources/text/upload", {
    method: "POST",
    body: {
      source_id: sourceId,
      name: sourceName,
      filename: file.name,
      file_content: fileContent,
      license_name: "User Supplied",
    },
  });

  setStoredOnboardingStep(2);
  await setPreferredBibleSource(descriptor.source_id, { successMessage: `${descriptor.name} is now your default Bible.` });
  sourceUi.uploadForm.reset();
}

async function onConnectBibleApiSource(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to connect a real Bible source.")) {
    return;
  }

  const sourceUi = bibleSourceElements();
  const sourceName = optionalText(sourceUi.apiName.value);
  const baseUrl = optionalText(sourceUi.apiUrl.value);
  if (!sourceName || !baseUrl) {
    showToast("Add a provider name and base URL first.");
    return;
  }

  const descriptor = await fetchJson("/v1/sources/text/api", {
    method: "POST",
    body: {
      source_id: buildGeneratedSourceId(sourceName),
      name: sourceName,
      base_url: baseUrl,
      api_key: optionalText(sourceUi.apiKey.value),
      license_name: "User Supplied",
    },
  });

  setStoredOnboardingStep(2);
  await setPreferredBibleSource(descriptor.source_id, { successMessage: `${descriptor.name} is now your default Bible.` });
  sourceUi.apiForm.reset();
}

async function setPreferredBibleSource(sourceId, { successMessage = "Bible source updated." } = {}) {
  if (!sourceId) {
    return;
  }
  if (!ensureLiveMode("Switch to Live to update your default Bible source.")) {
    return;
  }

  await fetchJson(`/v1/users/${encodeURIComponent(getUserId())}/preferences`, {
    method: "PATCH",
    body: { preferred_translation_source_id: sourceId },
  });
  await loadTextSources();
  await refreshExperience({ restoreScreen: false });
  showToast(successMessage);
}

function buildSourceIdCandidate(value) {
  return String(value || "source")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    || "source";
}

function buildGeneratedSourceId(value) {
  return `${buildSourceIdCandidate(value)}_${Date.now()}`;
}




























