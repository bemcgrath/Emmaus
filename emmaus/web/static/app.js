const DEFAULT_TEXT_SOURCES = [
  { source_id: "sample_local", name: "Sample Public Domain Local Source" },
  { source_id: "user_api_placeholder", name: "User API Placeholder" },
];

const DEMO_SCENARIO_LABELS = {
  live: "Live data",
  first_visit: "First visit",
  in_progress: "In progress session",
  overdue_action: "Overdue action item",
  scheduled_nudge: "Scheduled nudge",
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
  onboardingStep: 1,
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
    demoSceneRow: document.getElementById("demo-scene-row"),
    demoStatusCopy: document.getElementById("demo-status-copy"),
    onboardingPanel: document.getElementById("onboarding-panel"),
    onboardingCopy: document.getElementById("onboarding-copy"),
    onboardingStepPill: document.getElementById("onboarding-step-pill"),
    onboardingFlow: document.getElementById("onboarding-flow"),
    todayPlanPill: document.getElementById("today-plan-pill"),
    todayPlanCard: document.getElementById("today-plan-card"),
    memoryThreadPill: document.getElementById("memory-thread-pill"),
    memoryThreadCard: document.getElementById("memory-thread-card"),
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
    completionSummaryPill: document.getElementById("completion-summary-pill"),
    completionSummaryCard: document.getElementById("completion-summary-card"),
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
  elements.demoSceneRow.addEventListener("click", onDemoScenarioSelect);
  elements.refreshButton.addEventListener("click", () => refreshExperience({ restoreScreen: false }).catch(handleError));
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
  elements.moodChipRow.querySelectorAll(".choice-chip").forEach((chip) => chip.addEventListener("click", () => selectMood(chip.dataset.value)));
  elements.studyDaysRow.querySelectorAll(".choice-chip").forEach((chip) => chip.addEventListener("click", () => toggleStudyDay(chip.dataset.day)));
}

function initializeDefaults() {
  elements.userIdInput.value = state.userId;
  state.onboardingStep = getStoredOnboardingStep();
  selectMood(state.selectedMood);
  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (browserTimezone) {
    elements.timezoneInput.placeholder = browserTimezone;
  }
  renderDemoControls();
}

async function loadApp() {
  await loadTextSources();
  await refreshExperience({ restoreScreen: true });
}

async function refreshExperience({ restoreScreen = false } = {}) {
  if (isDemoMode()) {
    renderDemoDashboard({ restoreScreen });
    return;
  }
  await loadLiveDashboard({ restoreScreen });
}

async function loadTextSources() {
  if (isDemoMode()) {
    state.textSources = DEFAULT_TEXT_SOURCES;
    renderTextSourceOptions();
    return;
  }
  try {
    const response = await fetchJson("/v1/sources/text");
    state.textSources = response.sources || response;
  } catch {
    state.textSources = DEFAULT_TEXT_SOURCES;
  }
  renderTextSourceOptions();
}

function renderTextSourceOptions() {
  const options = (state.textSources.length ? state.textSources : DEFAULT_TEXT_SOURCES)
    .map((source) => `<option value="${escapeHtml(source.source_id)}">${escapeHtml(source.name)}</option>`)
    .join("");
  elements.textSourceSelect.innerHTML = options;
  elements.preferredSourceSelect.innerHTML = options;
}

async function loadLiveDashboard({ restoreScreen = false } = {}) {
  const userId = getUserId();
  localStorage.setItem("emmaus.userId", userId);
  const [profile, recommendation, streaks, actionItems, latestMood, activeSession] = await Promise.all([
    fetchJson(`/v1/users/${encodeURIComponent(userId)}/profile`),
    fetchJson(`/v1/agent/recommendations/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/engagement/streaks/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/action-items/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/mood/${encodeURIComponent(userId)}`, { allowNull: true }),
    fetchJson(`/v1/agent/session/active/${encodeURIComponent(userId)}`, { allowNull: true }),
    fetchJson(`/v1/users/${encodeURIComponent(userId)}/memory`),
  ]);

  state.profile = profile;
  state.recommendation = recommendation;
  state.activeSessionPayload = activeSession;
  state.nudgePlan = null;

  renderDashboardShell({
    profile,
    recommendation,
    streaks,
    actionItems: actionItems.items || [],
    latestMood,
    activeSession,
    memorySummary,
  });

  await loadNudgeArtifacts();
  renderTodayPlan(recommendation, activeSession, actionItems.items || []);
  if (restoreScreen) {
    restorePreferredScreen();
  }
}

function renderDemoDashboard({ restoreScreen = false } = {}) {
  const demo = buildDemoScenarioData(state.demoScenario);
  state.profile = demo.profile;
  state.recommendation = demo.recommendation;
  state.activeSessionPayload = demo.activeSession;
  state.nudge = demo.nudge;
  state.nudgePlan = demo.nudgePlan;
  state.memorySummary = demo.memorySummary;
  renderDashboardShell({
    profile: demo.profile,
    recommendation: demo.recommendation,
    streaks: demo.streaks,
    actionItems: demo.actionItems,
    latestMood: demo.latestMood,
    activeSession: demo.activeSession,
    memorySummary: demo.memorySummary,
  });
  renderNudge(demo.nudge, demo.nudgePlan);
  renderTodayPlan(demo.recommendation, demo.activeSession, demo.actionItems, demo.memorySummary);
  if (restoreScreen) {
    restorePreferredScreen();
  }
}

function renderDashboardShell({ profile, recommendation, streaks, actionItems, latestMood, activeSession, memorySummary }) {
  renderProfile(profile);
  renderRecommendation(recommendation);
  renderMemorySummary(memorySummary);
  renderStreaks(streaks);
  renderActionItems(actionItems);
  renderCompletionSummary(memorySummary, actionItems);
  renderLatestMood(latestMood);
  renderOnboarding(profile, streaks, activeSession);
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

function getInitialDemoScenario() {
  const params = new URLSearchParams(window.location.search);
  const fromUrl = normalizeDemoScenario(params.get("demo"));
  if (fromUrl) {
    localStorage.setItem("emmaus.demoScenario", fromUrl);
    return fromUrl;
  }
  return normalizeDemoScenario(localStorage.getItem("emmaus.demoScenario")) || "first_visit";
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
      preferred_translation_source_id: "sample_local",
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
        "Open action items suggest follow-through needs a little reinforcement.",
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
      text_source_id: "sample_local",
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
      source_id: "sample_local",
      translation_name: "Sample Public Domain Local Source",
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
        growth_areas: ["closing the loop on action items", "restarting gently after missing a few days"],
        carry_forward_prompt: "Follow through on the encouragement Emmaus already surfaced before you begin something new.",
      },
      nudge: {
        ...scheduledNudge,
        nudge_type: "follow_through",
        title: "Follow through on your last step",
        message: "Before starting something new, finish what your last session already surfaced.",
        timing_decision: "now",
        timing_reason: "The user is in a valid study window and an unfinished action item is waiting.",
        scheduled_for: null,
      },
      nudgePlan: {
        ...scheduledPlan,
        delivery_status: "send_now",
        deliver_at: "2026-04-05T12:30:00-04:00",
        fallback_at: "2026-04-05T12:30:00-04:00",
        idempotency_key: "demo-user:follow_through:continue where I left off:2026-04-05T12:30:00-04:00",
        reason: "A follow-through reminder can be sent immediately because the action item is overdue and the user is available.",
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

  elements.textSourceSelect.innerHTML = options;
  elements.preferredSourceSelect.innerHTML = options;

  const preferredSource = state.profile?.preferences?.preferred_translation_source_id || sources[0]?.source_id || "";
  const sessionSource = state.activeSessionPayload?.session?.text_source_id || preferredSource;

  if (preferredSource) {
    elements.preferredSourceSelect.value = preferredSource;
  }
  if (sessionSource) {
    elements.textSourceSelect.value = sessionSource;
  }
}

async function loadLiveDashboard({ restoreScreen = false } = {}) {
  const userId = getUserId();
  state.userId = userId;
  localStorage.setItem("emmaus.userId", userId);

  const [profile, recommendation, streaks, actionItemsResponse, latestMood, activeSession, memorySummary] = await Promise.all([
    fetchJson(`/v1/users/${encodeURIComponent(userId)}/profile`),
    fetchJson(`/v1/agent/recommendations/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/engagement/streaks/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/action-items/${encodeURIComponent(userId)}`),
    fetchJson(`/v1/study/mood/${encodeURIComponent(userId)}`, { allowNull: true }),
    fetchJson(`/v1/agent/session/active/${encodeURIComponent(userId)}`, { allowNull: true }),
  ]);

  state.profile = profile;
  state.recommendation = recommendation;
  state.streaks = streaks;
  state.actionItems = actionItemsResponse.items || [];
  state.latestMood = latestMood;
  state.activeSessionPayload = activeSession;
  state.currentQuestion = activeSession?.current_question || null;
  state.memorySummary = memorySummary;
  state.nudge = null;
  state.nudgePlan = null;

  renderDashboardShell({
    profile,
    recommendation,
    streaks,
    actionItems: state.actionItems,
    latestMood,
    activeSession,
  });

  await loadNudgeArtifacts();
  renderTodayPlan(recommendation, activeSession, state.actionItems, memorySummary);
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
  state.latestMood = demo.latestMood;
  state.activeSessionPayload = demo.activeSession;
  state.currentQuestion = demo.activeSession?.current_question || null;
  state.nudge = demo.nudge;
  state.nudgePlan = demo.nudgePlan;

  renderDashboardShell({
    profile: demo.profile,
    recommendation: demo.recommendation,
    streaks: demo.streaks,
    actionItems: demo.actionItems,
    latestMood: demo.latestMood,
    activeSession: demo.activeSession,
  });
  renderNudge(demo.nudge, demo.nudgePlan);
  renderTodayPlan(demo.recommendation, demo.activeSession, demo.actionItems);
  if (restoreScreen) {
    restorePreferredScreen();
  }
}

function renderDashboardShell({ profile, recommendation, streaks, actionItems, latestMood, activeSession }) {
  renderHero(profile, recommendation, activeSession, actionItems);
  renderProfile(profile);
  renderRecommendation(recommendation);
  renderStreaks(streaks);
  renderActionItems(actionItems);
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
    elements.heroCopy.textContent = "Emmaus is surfacing your unfinished action item first so reflection becomes real follow-through.";
    elements.heroPrimaryButton.textContent = "Review Action Item";
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
    ? `Emmaus is steering today's session toward ${recommendation.focus_area} so the next study meets your real pattern, not a generic plan.`
    : "Emmaus adapts each session to your habits, understanding, and next step of obedience.";
  elements.heroPrimaryButton.textContent = "Start Today's Plan";
}

function renderProfile(profile) {
  const preferences = profile?.preferences || {};
  elements.userIdInput.value = profile?.user_id || state.userId;
  elements.displayNameInput.value = profile?.display_name || "";
  elements.preferredMinutesInput.value = preferences.preferred_session_minutes || "";
  elements.guideModeSelect.value = preferences.preferred_guide_mode || "guide";
  elements.nudgeIntensitySelect.value = preferences.nudge_intensity || "balanced";
  elements.timezoneInput.value = preferences.timezone || "";
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

function renderRecommendation(recommendation) {
  if (!recommendation) {
    elements.focusPill.textContent = "Waiting";
    elements.recommendationCard.innerHTML = '<p class="empty-state">No recommendation is available yet.</p>';
    return;
  }

  elements.focusPill.textContent = sentenceCase(recommendation.focus_area);
  const patterns = safeArray(recommendation.gap_report?.observed_patterns)
    .map((pattern) => `<span class="meta-pill">${escapeHtml(pattern)}</span>`)
    .join("");

  elements.recommendationCard.innerHTML = `
    <div class="recommendation-card">
      <p><strong>${escapeHtml(formatReference(recommendation.recommended_reference))}</strong></p>
      <p>${escapeHtml(recommendation.reason)}</p>
      <div class="recommendation-meta">
        <span class="meta-pill">${escapeHtml(sentenceCase(recommendation.recommended_guide_mode))}</span>
        <span class="meta-pill">${escapeHtml(String(recommendation.recommended_minutes))} min</span>
        <span class="meta-pill">${escapeHtml(recommendation.recommended_entry_point)}</span>
      </div>
      <p><strong>Suggested application:</strong> ${escapeHtml(recommendation.suggested_action)}</p>
      ${patterns ? `<div class="content-stack">${patterns}</div>` : ""}
    </div>
  `;
}

function renderMemorySummary(memorySummary) {
  if (!memorySummary || !memorySummary.memory_count) {
    elements.memoryThreadPill.textContent = "Ready";
    elements.memoryThreadCard.innerHTML = `
      <div class="memory-card">
        <p><strong>Emmaus will start tracking your growth here.</strong></p>
        <p class="today-plan-copy">Complete a session and Emmaus will carry forward the themes, growth edges, and next thread to revisit.</p>
      </div>
    `;
    return;
  }

  elements.memoryThreadPill.textContent = `${memorySummary.memory_count} ${memorySummary.memory_count === 1 ? "thread" : "threads"}`;
  const themes = safeArray(memorySummary.recurring_themes)
    .map((theme) => `<span class="meta-pill">${escapeHtml(theme)}</span>`)
    .join("");
  const growthAreas = safeArray(memorySummary.growth_areas)
    .map((area) => `<span class="meta-pill">${escapeHtml(area)}</span>`)
    .join("");
  const references = safeArray(memorySummary.recent_references)
    .map((reference) => `<span class="meta-pill">${escapeHtml(reference)}</span>`)
    .join("");

  elements.memoryThreadCard.innerHTML = `
    <div class="memory-card">
      <p><strong>${escapeHtml(memorySummary.latest_summary || "Emmaus is carrying a recent thread forward.")}</strong></p>
      ${themes ? `<div class="memory-theme-list">${themes}</div>` : ""}
      ${growthAreas ? `<p><strong>Growth edges:</strong> ${growthAreas}</p>` : ""}
      ${memorySummary.carry_forward_prompt ? `<p class="memory-prompt">${escapeHtml(memorySummary.carry_forward_prompt)}</p>` : ""}
      ${references ? `<div class="today-plan-actions">${references}</div>` : ""}
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
    elements.onboardingCopy.textContent = "Tell Emmaus the best time of day to reach you so today?s plan and future nudges fit your rhythm.";
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

  elements.onboardingCopy.textContent = "Your starter rhythm is ready. Emmaus can launch today?s first guided session now.";
  const recommendation = state.recommendation;
  elements.onboardingFlow.innerHTML = `
    <div class="today-plan-card onboarding-step-card">
      <p><strong>Start your first session</strong></p>
      <p class="today-plan-copy">${escapeHtml(recommendation ? recommendation.reason : "Emmaus is ready with a first guided session.")}</p>
      <div class="today-plan-actions">
        <span class="meta-pill">${escapeHtml(String(recommendation?.recommended_minutes || state.profile?.preferences?.preferred_session_minutes || 15))} min</span>
        <span class="meta-pill">${escapeHtml(sentenceCase(recommendation?.recommended_guide_mode || "guide"))}</span>
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

function updateSessionEntryState(activeSession) {
  if (activeSession) {
    const session = activeSession.session;
    elements.sessionStatusPill.textContent = "Active";
    elements.sessionFormCopy.textContent = `You already have an active session in ${formatReference(session.reference)}. Continue it below.`;
    elements.sessionFormButton.textContent = "Continue current session";
    elements.entryPointInput.value = session.entry_point || state.recommendation?.recommended_entry_point || "continue where I left off";
    elements.requestedMinutesInput.value = session.requested_minutes || state.recommendation?.recommended_minutes || "";
    elements.sessionGuideMode.value = session.guide_mode || "";
    if (session.text_source_id) {
      elements.textSourceSelect.value = session.text_source_id;
    }
    return;
  }

  elements.sessionStatusPill.textContent = "Ready";
  elements.sessionFormCopy.textContent = state.recommendation
    ? `Emmaus suggests ${state.recommendation.recommended_minutes} minutes focused on ${state.recommendation.focus_area}.`
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
function renderTodayPlan(recommendation, activeSession, actionItems, memorySummary) {
  const openAction = actionItems.find((item) => item.status === "open");
  const carryForwardPrompt = memorySummary?.carry_forward_prompt || null;

  if (activeSession) {
    const session = activeSession.session;
    elements.todayPlanPill.textContent = "Resume";
    elements.todayPlanCard.dataset.action = "resume_session";
    elements.todayPlanCard.innerHTML = `
      <div class="today-plan-card">
        <p><strong>${escapeHtml(formatReference(session.reference))}</strong></p>
        <p class="today-plan-copy">${escapeHtml(session.latest_message)}</p>
        ${carryForwardPrompt ? `<p class="memory-prompt">${escapeHtml(carryForwardPrompt)}</p>` : ""}
        <div class="today-plan-actions">
          <span class="meta-pill">${escapeHtml(buildQuestionProgress(session))}</span>
          <span class="meta-pill">${escapeHtml(sentenceCase(session.guide_mode))}</span>
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
          <span class="meta-pill">Action item</span>
        </div>
        <button class="primary-button full-width" type="button">Record follow-through</button>
      </div>
    `;
    return;
  }

  if (recommendation) {
    elements.todayPlanPill.textContent = sentenceCase(recommendation.focus_area);
    elements.todayPlanCard.dataset.action = "start_session";
    elements.todayPlanCard.innerHTML = `
      <div class="today-plan-card">
        <p><strong>${escapeHtml(formatReference(recommendation.recommended_reference))}</strong></p>
        <p class="today-plan-copy">${escapeHtml(recommendation.reason)}</p>
        ${carryForwardPrompt ? `<p class="memory-prompt"><strong>Continue this thread:</strong> ${escapeHtml(carryForwardPrompt)}</p>` : ""}
        <div class="today-plan-actions">
          <span class="meta-pill">${escapeHtml(sentenceCase(recommendation.recommended_guide_mode))}</span>
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
  const beforeSummary = followThroughUpdate?.beforeMemorySummary?.latest_summary || null;
  const beforePrompt = followThroughUpdate?.beforeMemorySummary?.carry_forward_prompt || null;
  const changeSummary = beforeSummary && beforeSummary !== latestSummary
    ? `<p class="session-context-copy"><strong>Updated thread:</strong> ${escapeHtml(beforeSummary)} -> ${escapeHtml(latestSummary)}</p>`
    : "";
  const changePrompt = beforePrompt && beforePrompt !== carryForwardPrompt
    ? `<p class="session-context-copy"><strong>New carry-forward:</strong> ${escapeHtml(carryForwardPrompt || "")}</p>`
    : "";
  const followThroughNote = followThroughUpdate?.actionItem?.follow_up_note
    ? `<p class="session-context-copy"><strong>What landed:</strong> ${escapeHtml(followThroughUpdate.actionItem.follow_up_note)}</p>`
    : "";

  elements.completionSummaryCard.innerHTML = `
    <div class="completion-card">
      <p><strong>${followThroughUpdate ? "Emmaus updated this thread" : "What Emmaus noticed"}</strong></p>
      <p class="today-plan-copy">${escapeHtml(latestSummary)}</p>
      ${changeSummary}
      ${growthArea ? `<p><strong>Growth edge:</strong> ${escapeHtml(growthArea)}</p>` : ""}
      ${carryForwardPrompt ? `<p class="memory-prompt"><strong>Emmaus will carry forward:</strong> ${escapeHtml(carryForwardPrompt)}</p>` : ""}
      ${changePrompt}
      ${followThroughNote}
      <div class="inline-card">
        <p><strong>${escapeHtml(actionTitle)}</strong></p>
        <p>${escapeHtml(actionDetail)}</p>
        ${actionCreatedAt ? `<span class="meta-pill">Created ${escapeHtml(actionCreatedAt)}</span>` : ""}
        ${followThroughUpdate?.actionItem?.follow_up_outcome ? `<span class="meta-pill">${escapeHtml(sentenceCase(followThroughUpdate.actionItem.follow_up_outcome.replaceAll("_", " ")))}</span>` : ""}
      </div>
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
    elements.actionItemList.innerHTML = '<p class="empty-state">No action items yet. Complete a session and Emmaus will place your next step here.</p>';
    return;
  }

  elements.actionItemList.innerHTML = actionItems
    .map((item) => {
      const isSelected = item.action_item_id === state.selectedActionItemId;
      const completed = item.status === "completed";
      const footer = completed
        ? `<p class="micro-copy">Completed ${escapeHtml(formatDateTime(item.completed_at))}${item.follow_up_outcome ? ` � ${escapeHtml(sentenceCase(item.follow_up_outcome.replaceAll("_", " ")) )}` : ""}</p>${item.follow_up_note ? `<p>${escapeHtml(item.follow_up_note)}</p>` : ""}`
        : `<button class="action-button" type="button" data-action-item-select="${escapeHtml(item.action_item_id)}">${isSelected ? "Selected for follow-up" : "Complete follow-through"}</button>`;
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
    })
    .join("");
}

function syncSelectedActionItem(actionItems) {
  const openItems = actionItems.filter((item) => item.status === "open");
  const selected = openItems.find((item) => item.action_item_id === state.selectedActionItemId) || openItems[0] || null;
  state.selectedActionItemId = selected?.action_item_id || null;

  if (!selected) {
    elements.followUpTargetCopy.textContent = "Select an open action item above to complete it with a short reflection.";
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
  const reason = recommendation?.reason || "Emmaus has shaped this session around what seems most helpful for your next step with Christ.";
  const carryForwardPrompt = memorySummary?.carry_forward_prompt || null;
  const leadingPattern = safeArray(recommendation?.gap_report?.observed_patterns)[0] || null;
  const meta = [
    recommendation?.focus_area ? `<span class="meta-pill">${escapeHtml(sentenceCase(recommendation.focus_area))}</span>` : "",
    recommendation?.recommended_guide_mode ? `<span class="meta-pill">${escapeHtml(sentenceCase(recommendation.recommended_guide_mode))}</span>` : "",
    recommendation?.recommended_minutes ? `<span class="meta-pill">${escapeHtml(String(recommendation.recommended_minutes))} min</span>` : "",
  ].filter(Boolean).join("");

  return `
    <div class="session-context-card">
      <p><strong>Why Emmaus brought you here today</strong></p>
      <p class="session-context-copy">${escapeHtml(reason)}</p>
      ${carryForwardPrompt ? `<p class="memory-prompt"><strong>Continuing thread:</strong> ${escapeHtml(carryForwardPrompt)}</p>` : ""}
      ${leadingPattern ? `<p class="session-context-copy"><strong>Watching for:</strong> ${escapeHtml(leadingPattern)}</p>` : ""}
      ${meta ? `<div class="session-meta">${meta}</div>` : ""}
    </div>
  `;
}

function renderSessionStart(payload, { navigate = true } = {}) {
  state.activeSessionPayload = payload;
  state.currentQuestion = payload.current_question || null;

  const session = payload.session;
  elements.sessionStatusPill.textContent = sentenceCase(session.status);
  elements.sessionReference.textContent = formatReference(session.reference);
  elements.questionProgressPill.textContent = buildQuestionProgress(session);
  elements.sessionHero.innerHTML = `
    ${buildSessionContextCard(payload)}
    <div class="inline-card">
      <p><strong>${escapeHtml(sentenceCase(session.guide_mode))} mode</strong></p>
      <p>${escapeHtml(session.latest_message || "Emmaus is ready to guide this session.")}</p>
      <div class="session-meta">
        <span class="meta-pill">${escapeHtml(String(session.requested_minutes))} min</span>
        <span class="meta-pill">${escapeHtml(session.entry_point)}</span>
      </div>
    </div>
  `;
  elements.passageText.textContent = payload.passage?.text || "No passage is available yet.";
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
  elements.commentaryBlock.innerHTML = safeArray(payload.commentary).length
    ? safeArray(payload.commentary)
        .map(
          (note) => `
            <div class="commentary-note">
              <p><strong>${escapeHtml(note.title)}</strong></p>
              <p>${escapeHtml(note.body)}</p>
            </div>
          `,
        )
        .join("")
    : "";

  if (state.currentQuestion) {
    elements.currentQuestionHeading.textContent = `${sentenceCase(state.currentQuestion.type)} question`;
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

  elements.entryPointInput.value = session.entry_point || state.recommendation?.recommended_entry_point || "continue where I left off";
  elements.requestedMinutesInput.value = session.requested_minutes || state.recommendation?.recommended_minutes || "";
  elements.sessionGuideMode.value = session.guide_mode || "";
  if (session.text_source_id) {
    elements.textSourceSelect.value = session.text_source_id;
  }

  if (navigate) {
    showScreen("session");
  }
}

function clearSessionView() {
  state.activeSessionPayload = null;
  state.currentQuestion = null;
  elements.sessionReference.textContent = "No active session yet";
  elements.questionProgressPill.textContent = "0 / 0";
  elements.sessionHero.innerHTML = '<p class="empty-state">Start a session to see the passage, plan, and first question.</p>';
  elements.passageText.textContent = "Start a session to see the passage, plan, and first question.";
  elements.sessionPlan.innerHTML = '<p class="empty-state">Your study plan will appear here once a session starts.</p>';
  elements.commentaryBlock.innerHTML = "";
  elements.currentQuestionHeading.textContent = "Current question";
  elements.currentQuestionCopy.textContent = "Emmaus will place the next question here.";
  elements.responseText.value = "";
  elements.responseText.disabled = true;
  elements.engagementInput.value = 4;
  elements.engagementInput.disabled = true;
  elements.submitResponseButton.disabled = true;
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

function renderNudge(nudge, nudgePlan) {
  const statusCopy = nudgePlan?.delivery_status ? sentenceCase(nudgePlan.delivery_status.replaceAll("_", " ")) : sentenceCase(nudge?.timing_decision || "checking");
  elements.nudgeTimingPill.textContent = statusCopy;

  if (!nudge) {
    elements.nudgeCard.innerHTML = '<p class="empty-state">No nudge preview is available right now.</p>';
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
        <span class="meta-pill">${escapeHtml(sentenceCase(nudge.nudge_type.replaceAll("_", " ")) )}</span>
        <span class="meta-pill">${escapeHtml(String(nudge.recommended_minutes))} min</span>
        <span class="meta-pill">${escapeHtml(sentenceCase(nudge.recommended_guide_mode))}</span>
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
      <p class="panel-label">Why this nudge</p>
      <p>${reasonLine}</p>
      ${followThroughLine}
      ${promptLine}
    </div>
  `;
}

function renderDemoControls() {
  const label = DEMO_SCENARIO_LABELS[state.demoScenario] || DEMO_SCENARIO_LABELS.first_visit;
  elements.demoStatusCopy.textContent = isDemoMode()
    ? `Showing ${label}. Demo scenes are read-only and never write to your live Emmaus data.`
    : "Live mode is using the real API-backed data for the current user. Switch to a seeded demo scene anytime.";

  elements.demoSceneRow.querySelectorAll("[data-demo-scenario]").forEach((button) => {
    button.classList.toggle("choice-chip-active", button.dataset.demoScenario === state.demoScenario);
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

function onHeroPrimaryAction() {
  onTodayPlanAction();
}

function onTodayPlanAction() {
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
    await setPreferredBibleSource("sample_local", { successMessage: "Starter Bible selected." });
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
    if (sourceUi.advancedPanel?.classList.contains("hidden")) {
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
    completeOnboarding();
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
    preferred_translation_source_id: optionalText(elements.preferredSourceSelect.value),
    nudge_intensity: optionalText(elements.nudgeIntensitySelect.value),
    timezone: optionalText(elements.timezoneInput.value) || Intl.DateTimeFormat().resolvedOptions().timeZone || null,
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
    if (fromOnboarding) {
      completeOnboarding();
    }
    showScreen("session");
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
  renderTodayPlan(state.recommendation, payload, state.actionItems);
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
  showToast("Session completed. Your action item is ready.");
}

async function onSubmitActionFollowUp(event) {
  event.preventDefault();
  if (!ensureLiveMode("Switch to Live to save a real follow-through note.")) {
    return;
  }
  if (!state.selectedActionItemId) {
    showToast("Select an action item first.");
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
  showToast("Follow-through saved. Emmaus updated your thread.");
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
  showToast(previewAt ? "Nudge timing refreshed for the selected time." : "Nudge timing refreshed.");
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
  state.activeScreen = screenName;
  localStorage.setItem("emmaus.activeScreen", screenName);
  elements.screens.forEach((screen) => {
    screen.classList.toggle("screen-active", screen.dataset.screen === screenName);
  });
  elements.navButtons.forEach((button) => {
    button.classList.toggle("nav-pill-active", button.dataset.navTarget === screenName);
  });
}

function focusIdentityForm() {
  showScreen("home");
  if (!elements.onboardingPanel.classList.contains("hidden")) {
    elements.onboardingPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  elements.identityForm.scrollIntoView({ behavior: "smooth", block: "start" });
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

function formatReference(reference) {
  if (!reference) {
    return "Unknown reference";
  }
  const endVerse = reference.end_verse ? `-${reference.end_verse}` : "";
  return `${reference.book} ${reference.chapter}:${reference.start_verse}${endVerse}`;
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
    return "0 / 0";
  }
  const current = Math.min(session.current_question_index + 1, total);
  return `${current} / ${total}`;
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
    library: document.getElementById("source-library"),
    copy: document.getElementById("source-manager-copy"),
    useStarterButton: document.getElementById("source-use-starter"),
    advancedToggle: document.getElementById("source-advanced-toggle"),
    advancedPanel: document.getElementById("source-advanced-panel"),
    uploadForm: document.getElementById("source-upload-form"),
    uploadName: document.getElementById("source-upload-name"),
    uploadFile: document.getElementById("source-upload-file"),
    apiForm: document.getElementById("source-api-form"),
    apiName: document.getElementById("source-api-name"),
    apiUrl: document.getElementById("source-api-url"),
    apiKey: document.getElementById("source-api-key"),
  };
}

document.addEventListener("DOMContentLoaded", () => {
  const sourceUi = bibleSourceElements();
  sourceUi.library?.addEventListener("click", onSourceLibraryClick);
  sourceUi.useStarterButton?.addEventListener("click", onUseStarterBible);
  sourceUi.advancedToggle?.addEventListener("click", onToggleAdvancedBibleSetup);
  sourceUi.uploadForm?.addEventListener("submit", onUploadBibleSource);
  sourceUi.apiForm?.addEventListener("submit", onConnectBibleApiSource);
});

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

function renderTextSourceOptions() {
  const sources = state.textSources.length ? state.textSources : DEFAULT_TEXT_SOURCES;
  const options = sources
    .map((source) => `<option value="${escapeHtml(source.source_id)}">${escapeHtml(source.name)}</option>`)
    .join("");
  elements.textSourceSelect.innerHTML = options;
  elements.preferredSourceSelect.innerHTML = options;

  const preferredSourceId = state.profile?.preferences?.preferred_translation_source_id || sources[0]?.source_id || "";
  const sessionSourceId = state.activeSessionPayload?.session?.text_source_id || preferredSourceId;

  if (preferredSourceId) {
    elements.preferredSourceSelect.value = preferredSourceId;
  }
  if (sessionSourceId) {
    elements.textSourceSelect.value = sessionSourceId;
  }

  renderBibleSourceManager();
}

function renderProfile(profile) {
  const preferences = profile?.preferences || {};
  elements.userIdInput.value = profile?.user_id || state.userId;
  elements.displayNameInput.value = profile?.display_name || "";
  elements.preferredMinutesInput.value = preferences.preferred_session_minutes || "";
  elements.guideModeSelect.value = preferences.preferred_guide_mode || "guide";
  elements.nudgeIntensitySelect.value = preferences.nudge_intensity || "balanced";
  elements.timezoneInput.value = preferences.timezone || "";
  elements.studyWindowStartInput.value = preferences.preferred_study_window_start || "";
  elements.studyWindowEndInput.value = preferences.preferred_study_window_end || "";
  elements.quietHoursStartInput.value = preferences.quiet_hours_start || "";
  elements.quietHoursEndInput.value = preferences.quiet_hours_end || "";
  state.selectedStudyDays = Array.isArray(preferences.preferred_study_days) ? [...preferences.preferred_study_days] : [];
  updateStudyDayChips();
  renderTextSourceOptions();
}

function renderBibleSourceManager() {
  const sourceUi = bibleSourceElements();
  if (!sourceUi.library || !sourceUi.copy) {
    return;
  }

  const sources = (state.textSources.length ? state.textSources : DEFAULT_TEXT_SOURCES).filter(
    (source) => source.source_id !== "user_api_placeholder",
  );
  const preferredSourceId = state.profile?.preferences?.preferred_translation_source_id || elements.preferredSourceSelect?.value || "";
  const preferredSource = sources.find((source) => source.source_id === preferredSourceId) || null;
  const starterSource = sources.find((source) => source.source_id === "sample_local") || null;

  sourceUi.copy.textContent = preferredSource
    ? `Current Bible: ${preferredSource.name}. Pick another one any time.`
    : "Pick a Bible and start studying. You can always change it later.";

  if (sourceUi.useStarterButton) {
    const starterActive = preferredSourceId === "sample_local";
    sourceUi.useStarterButton.disabled = !starterSource || starterActive;
    sourceUi.useStarterButton.textContent = starterActive ? "Using included starter Bible" : "Use included starter Bible";
  }

  const connectedSources = sources.filter((source) => source.source_id !== "sample_local");
  if (!connectedSources.length) {
    sourceUi.library.innerHTML = '<p class="empty-state">No other Bibles are connected yet. You can start with the included Bible or upload one from this device.</p>';
    return;
  }

  sourceUi.library.innerHTML = connectedSources
    .map((source) => {
      const isPreferred = source.source_id === preferredSourceId;
      const providerLabel = source.provider_type === "remote_api" ? "Connected provider" : "Uploaded from this device";
      return `
        <article class="action-card ${isPreferred ? "selected" : ""}">
          <div class="action-card-header">
            <div>
              <p><strong>${escapeHtml(source.name)}</strong></p>
              <p>${escapeHtml(providerLabel)}</p>
            </div>
            <span class="status-pill">${isPreferred ? "Current" : "Ready"}</span>
          </div>
          <div class="source-card-actions">
            <button class="action-button" type="button" data-source-prefer="${escapeHtml(source.source_id)}" ${isPreferred ? "disabled" : ""}>${isPreferred ? "Using this Bible" : "Use this Bible"}</button>
          </div>
        </article>
      `;
    })
    .join("");
}

async function onSourceLibraryClick(event) {
  const button = event.target.closest("[data-source-prefer]");
  if (!button) {
    return;
  }
  await setPreferredBibleSource(button.dataset.sourcePrefer);
}

async function onUseStarterBible() {
  await setPreferredBibleSource("sample_local", { successMessage: "The included starter Bible is now your default." });
}

function onToggleAdvancedBibleSetup() {
  const sourceUi = bibleSourceElements();
  if (!sourceUi.advancedPanel || !sourceUi.advancedToggle) {
    return;
  }
  const willShow = sourceUi.advancedPanel.classList.contains("hidden");
  sourceUi.advancedPanel.classList.toggle("hidden", !willShow);
  sourceUi.advancedToggle.setAttribute("aria-expanded", willShow ? "true" : "false");
  sourceUi.advancedToggle.textContent = willShow ? "Hide setup options" : "More setup options";
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
