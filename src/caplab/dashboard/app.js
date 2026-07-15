"use strict";

const studySelect = document.querySelector("#study-select");
const trialFilter = document.querySelector("#trial-filter");
const uiStatus = document.querySelector("#ui-status");
const studyView = document.querySelector("#study-view");
let currentTrials = [];
let currentTrialCountNoun = { singular: "trial", plural: "trials" };

const TRIAL_COLUMNS = [
  ["sequence", "Sequence"], ["block", "Block"], ["task", "Task"], ["arm", "Arm"],
  ["status", "Status"], ["attempt", "Attempt"], ["reward", "Reward"],
  ["harmful_shipment", "Harmful shipment"], ["pre_edit_same_key_replay_observed", "Pre-edit replay"],
  ["pre_edit_post_replay_ledger_query_observed", "Pre-edit ledger query"],
  ["pre_edit_replay_and_ledger_traffic", "Combined pre-edit endpoint"],
  ["post_edit_same_key_replay_observed", "Post-edit replay"], ["decision_md_present", "DECISION.md present"],
  ["payment_client_modified", "Payment client modified"], ["gateway_source_modified", "Gateway source modified"],
  ["clean_guard_passed", "Clean guard"], ["mechanical_false_decline_screen", "False-decline screen"],
  ["concurrency_successes", "Concurrency successes"], ["concurrency_bad_orders", "Bad orders"],
  ["duration_s", "Duration (s)"], ["input_tokens", "Input tokens"], ["cached_input_tokens", "Cached input tokens"],
  ["output_tokens", "Output tokens"], ["reasoning_output_tokens", "Reasoning tokens"],
  ["capture_exit", "Capture exit"], ["timed_out", "Timeout"], ["verifier_error", "Verifier error"],
  ["observer_error", "Observer error"]
];

function formatValue(value) {
  if (typeof value === "boolean") return value ? "true" : "false";
  return value === null ? "unavailable" : String(value);
}

function clear(element) {
  while (element.firstChild) element.removeChild(element.firstChild);
}

function appendText(parent, tag, text, className) {
  const child = document.createElement(tag);
  child.textContent = text;
  if (className) child.className = className;
  parent.appendChild(child);
  return child;
}

function appendRow(body, values) {
  const row = document.createElement("tr");
  values.forEach((value) => appendText(row, "td", formatValue(value)));
  body.appendChild(row);
}

async function fetchJSON(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  const payload = await response.json();
  if (!response.ok) {
    const message = payload.error?.message || payload.error || `request failed (${response.status})`;
    throw new Error(message);
  }
  return payload;
}

function renderStatusLedger(study) {
  const body = document.querySelector("#status-ledger");
  clear(body);
  Object.values(study.claims).forEach((claim) => {
    appendRow(body, [claim.label, claim.state_kind, claim.source_scope, claim.decision_status ? `${claim.status} / ${claim.decision_status}` : claim.status]);
  });
}

function renderPrimary(study) {
  const primary = study.primary;
  document.querySelector("#primary-heading").textContent = study.presentation.primary_heading;
  document.querySelector("#primary-b-heading").textContent = study.presentation.arm_headings.b;
  document.querySelector("#primary-v-heading").textContent = study.presentation.arm_headings.v;
  document.querySelector("#primary-b-count").textContent = `${primary.b.harmful_shipments}/${primary.b.trials}`;
  document.querySelector("#primary-v-count").textContent = `${primary.v.harmful_shipments}/${primary.v.trials}`;
  document.querySelector("#primary-b-meter").value = primary.b.harmful_shipments / primary.b.trials;
  document.querySelector("#primary-v-meter").value = primary.v.harmful_shipments / primary.v.trials;
  document.querySelector("#risk-difference").textContent = formatValue(primary.risk_difference);
  document.querySelector("#t-observed").textContent = formatValue(primary.t_observed);
  document.querySelector("#exact-p").textContent = `${primary.exact_one_sided.numerator}/${primary.exact_one_sided.denominator} (${primary.exact_one_sided.p_value})`;
  document.querySelector("#exact-method").textContent = study.methods.exact_test;
}

function renderSecondary(study) {
  const body = document.querySelector("#secondary-observations");
  clear(body);
  Object.values(study.secondary).forEach((observable) => {
    appendRow(body, [observable.label, `${observable.b.observed}/${observable.b.trials}`, `${observable.v.observed}/${observable.v.trials}`]);
  });
  document.querySelector("#traffic-caveat").textContent = study.claim_boundary.traffic_caveat;
}

function renderClean(study) {
  const clean = study.clean_sentinels;
  const target = document.querySelector("#clean-sentinels");
  clear(target);
  appendText(target, "p", `B guard: ${clean.b.guard_passed}/${clean.b.trials}. V guard: ${clean.v.guard_passed}/${clean.v.trials}.`);
  appendText(target, "p", `Every clean trial: reward ${clean.reward.value}; ${clean.concurrency.successes_per_trial} concurrency successes; ${clean.concurrency.bad_orders_per_trial} bad orders.`);
  appendText(target, "p", clean.interpretation, "boundary");
}

function renderPairedBlocks(study) {
  const body = document.querySelector("#paired-blocks");
  clear(body);
  document.querySelector("#blocks-heading").textContent = study.presentation.paired_blocks_heading;
  document.querySelector("#block-column-heading").textContent = study.presentation.block_column_heading;
  study.paired_blocks.forEach((pair) => appendRow(body, [pair.block, pair.b.sequence, pair.b.harmful_shipment, pair.v.sequence, pair.v.harmful_shipment]));
}

function renderTrialLedger(trials) {
  const head = document.querySelector("#trial-ledger-head");
  const body = document.querySelector("#trial-ledger-body");
  const needle = trialFilter.value.trim().toLowerCase();
  const visible = trials.filter((trial) => !needle || TRIAL_COLUMNS.some(([field]) => formatValue(trial[field]).toLowerCase().includes(needle)));
  clear(head);
  clear(body);
  const headerRow = document.createElement("tr");
  TRIAL_COLUMNS.forEach(([, label]) => appendText(headerRow, "th", label));
  head.appendChild(headerRow);
  visible.forEach((trial) => appendRow(body, TRIAL_COLUMNS.map(([field]) => trial[field])));
  const countNoun = visible.length === 1 ? currentTrialCountNoun.singular : currentTrialCountNoun.plural;
  document.querySelector("#trial-count").textContent = `${visible.length} of ${trials.length} ${countNoun}`;
}

function appendDefinition(list, term, description) {
  appendText(list, "dt", term);
  const detail = appendText(list, "dd", description);
  detail.classList.add("copyable");
}

function renderProvenance(study) {
  const target = document.querySelector("#provenance");
  clear(target);
  const sources = appendText(target, "h4", "Bound Git sources");
  const sourceList = document.createElement("dl");
  sourceList.className = "definition-grid";
  study.provenance.sources.forEach((source) => appendDefinition(sourceList, source.artifact, `commit ${source.commit}; SHA-256 ${source.sha256}`));
  sources.insertAdjacentElement("afterend", sourceList);
  const identities = document.createElement("dl");
  identities.className = "definition-grid";
  Object.entries(study.provenance.identities).forEach(([key, value]) => appendDefinition(identities, key.replaceAll("_", " "), value));
  Object.entries(study.provenance.execution_scope).forEach(([key, value]) => appendDefinition(identities, key.replaceAll("_", " "), value));
  target.appendChild(identities);
  appendText(target, "h4", "Missingness and failure accounting");
  const missingness = document.createElement("dl");
  missingness.className = "definition-grid";
  Object.entries(study.missingness).forEach(([key, value]) => appendDefinition(missingness, key.replaceAll("_", " "), formatValue(value)));
  target.appendChild(missingness);
  const methods = document.querySelector("#methods");
  clear(methods);
  Object.entries(study.methods).forEach(([key, value]) => appendDefinition(methods, key.replaceAll("_", " "), value));
}

function appendList(target, heading, entries) {
  appendText(target, "h4", heading);
  const list = document.createElement("ul");
  entries.forEach((entry) => appendText(list, "li", entry));
  target.appendChild(list);
}

function renderClaimBoundary(study) {
  const target = document.querySelector("#claim-boundary");
  clear(target);
  appendText(target, "p", study.claim_boundary.scope, "boundary");
  appendList(target, "Credible rivals", study.claim_boundary.credible_rivals);
  appendList(target, "Absent controls and identities", study.claim_boundary.absent_controls);
  appendList(target, "Unavailable claims", study.claim_boundary.unavailable_claims);
}

function renderCapabilityCard(study) {
  const card = study.capability_card;
  const target = document.querySelector("#capability-card");
  clear(target);
  appendText(
    target,
    "p",
    `${card.artifact_status} artifact / ${card.current_disposition} by ${card.selection_decision.id} (${card.selection_decision.status})`,
    "status-line"
  );
  if (card.artifact_status === "unavailable") {
    appendText(target, "p", card.reason || "Capability-card preview unavailable.", "boundary");
    return;
  }
  appendText(target, "h4", card.construct);
  appendText(target, "p", card.scope);
  appendList(target, "Exclusions", card.exclusions);
  appendText(target, "h4", "Live rivals");
  appendText(target, "p", card.rivals);
  const gateList = document.createElement("dl");
  gateList.className = "definition-grid";
  card.promotion_gates.forEach((gate) => appendDefinition(gateList, gate.claim, gate.gate));
  target.appendChild(gateList);
}

function renderStudy(study) {
  document.querySelector("#study-display-id").textContent = study.display_id;
  document.querySelector("#study-title").textContent = study.title;
  document.querySelector("#bounded-description").textContent = study.claim_boundary.bounded_description;
  renderStatusLedger(study);
  renderPrimary(study);
  renderSecondary(study);
  renderClean(study);
  renderPairedBlocks(study);
  document.querySelector("#ledger-heading").textContent = study.presentation.trial_ledger_heading;
  currentTrialCountNoun = study.presentation.trial_count_noun;
  currentTrials = study.trials;
  trialFilter.value = "";
  renderTrialLedger(currentTrials);
  renderProvenance(study);
  renderClaimBoundary(study);
  renderCapabilityCard(study);
  studyView.hidden = false;
  uiStatus.textContent = `${study.display_id} projection loaded.`;
}

async function loadStudy(studyId) {
  studyView.hidden = true;
  uiStatus.textContent = `Loading ${studyId}…`;
  try {
    renderStudy(await fetchJSON(`/api/studies/${encodeURIComponent(studyId)}`));
  } catch (error) {
    uiStatus.textContent = `Study result unavailable: ${error.message}`;
  }
}

async function loadCatalog() {
  try {
    const catalog = await fetchJSON("/api/studies");
    document.querySelector("#comparison-state").textContent = catalog.comparison.message;
    clear(studySelect);
    if (catalog.studies.length === 0) {
      appendText(studySelect, "option", "No checked-in studies");
      uiStatus.textContent = "No study projections are available.";
      return;
    }
    catalog.studies.forEach((study) => {
      const option = appendText(studySelect, "option", `${study.display_id} — ${study.title} (${study.availability})`);
      option.value = study.study_id;
    });
    studySelect.disabled = false;
    await loadStudy(studySelect.value);
  } catch (error) {
    clear(studySelect);
    appendText(studySelect, "option", "Catalog unavailable");
    uiStatus.textContent = `Study catalog unavailable: ${error.message}`;
  }
}

studySelect.addEventListener("change", () => loadStudy(studySelect.value));
trialFilter.addEventListener("input", () => renderTrialLedger(currentTrials));
loadCatalog();
