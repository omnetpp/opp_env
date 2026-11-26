"use strict";

const FILTER_DIMS = ["project", "version", "country", "os", "arch"];
const DEFAULTS = { range: "90", group: "project", split: "", dep: "1", ci: "0", from: "", to: "" };
const CUSTOM_DEFAULT_DAYS = 90;
const MAX_SPLIT_SERIES = 6;
const MAX_BARS = 20;
const DAY_MS = 86400000;

const form = document.getElementById("filters");
const app = document.getElementById("app");
const regionNames = new Intl.DisplayNames(["en"], { type: "region" });
const numberFormat = new Intl.NumberFormat("en");

Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;

let timelineChart = null;
let barsChart = null;
let lastRender = null;
let renderSeq = 0;

// Colors follow the entity, not its rank: a value keeps its slot for the whole visit
// unless that slot is taken by another value currently on screen.
const slotAssignments = new Map();
function assignSlots(dim, values) {
  const key = (v) => dim + "\u0000" + v;
  const slots = new Map();
  const taken = new Set();
  for (const v of values) {
    const previous = slotAssignments.get(key(v));
    if (previous && !taken.has(previous)) {
      slots.set(v, previous);
      taken.add(previous);
    }
  }
  for (const v of values) {
    if (slots.has(v))
      continue;
    let slot = 1;
    while (taken.has(slot))
      slot++;
    slots.set(v, slot);
    taken.add(slot);
    slotAssignments.set(key(v), slot);
  }
  return slots;
}

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function label(dim, value) {
  if (value === "" || value === null || value === undefined)
    return dim === "project" ? "(unknown client)" : "(unknown)";
  if (dim === "country") {
    try { return `${regionNames.of(value)} (${value})`; } catch { return value; }
  }
  if (dim === "ci")
    return value ? "CI" : "Not CI";
  if (dim === "dependency")
    return value ? "As dependency" : "Requested";
  if (dim === "os")
    return { linux: "Linux", macos: "macOS", wsl: "WSL" }[value] ?? value;
  return String(value);
}

// ---- state <-> URL ----

function readState() {
  const q = new URLSearchParams(location.search);
  const state = {};
  for (const k of ["range", "group", "split", "dep", "ci", "from", "to", ...FILTER_DIMS])
    state[k] = q.get(k) ?? DEFAULTS[k] ?? "";
  return state;
}

function writeState(state) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(state))
    if (v !== "" && v !== DEFAULTS[k])
      q.set(k, v);
  if (state.project === "" && state.version !== "")
    q.delete("version");
  if (state.range !== "custom") {
    q.delete("from");
    q.delete("to");
  }
  const search = q.toString();
  history.replaceState(null, "", search ? `?${search}` : location.pathname);
}

// Version strings are only comparable within one project, so grouping, splitting and
// filtering by version requires a selected project.
function syncVersionAvailability() {
  const hasProject = form.elements.project.value !== "";
  form.elements.version.disabled = !hasProject;
  if (!hasProject)
    form.elements.version.value = "";
  for (const name of ["group", "split"]) {
    const select = form.elements[name];
    select.querySelector('option[value="version"]').disabled = !hasProject;
    if (!hasProject && select.value === "version")
      select.value = name === "group" ? "project" : "";
  }
}

function stateFromForm() {
  syncVersionAvailability();
  const state = {};
  for (const k of ["range", "group", "split", ...FILTER_DIMS])
    state[k] = form.elements[k].value;
  state.dep = form.elements.dep.checked ? "1" : "0";
  state.ci = form.elements.ci.checked ? "1" : "0";
  syncCustomRange();
  state.from = form.elements.from.value;
  state.to = form.elements.to.value;
  return state;
}

function syncCustomRange() {
  const custom = form.elements.range.value === "custom";
  for (const el of document.querySelectorAll(".custom-range"))
    el.hidden = !custom;
  if (!custom)
    return;
  const today = isoDate(Date.now());
  const { from, to } = form.elements;
  from.max = to.max = today;
  if (!to.value || to.value > today)
    to.value = today;
  if (!from.value)
    from.value = isoDate(Date.parse(to.value) - (CUSTOM_DEFAULT_DAYS - 1) * DAY_MS);
  if (from.value > to.value)
    [from.value, to.value] = [to.value, from.value];
}

// ---- API ----

function isoDate(ms) {
  return new Date(ms).toISOString().slice(0, 10);
}

// The selected period as ISO dates; from is null for "all time".
function dateSpan(state) {
  const today = isoDate(Date.now());
  if (state.range === "custom")
    return { from: state.from, to: state.to };
  if (state.range === "all")
    return { from: null, to: today };
  return { from: isoDate(Date.now() - (Number(state.range) - 1) * DAY_MS), to: today };
}

function bucketFor(state) {
  const { from, to } = dateSpan(state);
  if (!from)
    return "month";
  const days = (Date.parse(to) - Date.parse(from)) / DAY_MS + 1;
  return days <= 92 ? "day" : days <= 731 ? "week" : "month";
}

function baseParams(state, { withFilters = true } = {}) {
  const p = new URLSearchParams();
  const span = dateSpan(state);
  if (span.from)
    p.set("from", span.from);
  if (state.range === "custom")
    p.set("to", span.to);
  if (state.ci === "0")
    p.set("ci", "0");
  if (state.dep === "0")
    p.set("dependency", "0");
  if (withFilters)
    for (const d of FILTER_DIMS)
      if (state[d] !== "" && (d !== "version" || state.project !== ""))
        p.set(d, state[d]);
  return p;
}

async function api(params) {
  const response = await fetch(`api?${params}`, { redirect: "manual" });
  // Only Cloudflare Access redirects here, once the session has expired. Fetch cannot follow it to the
  // login page, but a reload of the page can, and the state is kept in the URL.
  if (response.type === "opaqueredirect") {
    location.reload();
    return new Promise(() => {});
  }
  if (!(response.headers.get("content-type") || "").startsWith("application/json"))
    throw new Error(`unexpected response (HTTP ${response.status})`);
  const body = await response.json();
  if (!response.ok)
    throw new Error(body.error || response.statusText);
  return body.rows;
}

// ---- time axis ----

function timeBuckets(bucket, state, rows) {
  const span = dateSpan(state);
  const today = new Date(span.to + "T00:00:00Z");
  let start;
  if (span.from)
    start = new Date(span.from + "T00:00:00Z");
  else {
    const keys = rows.map((r) => r[bucket]).sort();
    start = keys.length ? new Date((keys[0].length === 7 ? keys[0] + "-01" : keys[0]) + "T00:00:00Z") : today;
  }
  const out = [];
  if (bucket === "day") {
    for (let t = start.getTime(); t <= today.getTime(); t += DAY_MS)
      out.push(isoDate(t));
  }
  else if (bucket === "week") {
    const monday = start.getTime() - ((start.getUTCDay() + 6) % 7) * DAY_MS;
    for (let t = monday; t <= today.getTime(); t += 7 * DAY_MS)
      out.push(isoDate(t));
  }
  else {
    const d = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth(), 1));
    while (d <= today) {
      out.push(isoDate(d.getTime()).slice(0, 7));
      d.setUTCMonth(d.getUTCMonth() + 1);
    }
  }
  return out;
}

function formatDate(iso) {
  return new Date(iso + "T00:00:00Z").toLocaleDateString("en", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
}

function formatBucket(bucket, key) {
  const date = new Date((key.length === 7 ? key + "-01" : key) + "T00:00:00Z");
  if (bucket === "month")
    return date.toLocaleDateString("en", { month: "short", year: "numeric", timeZone: "UTC" });
  return date.toLocaleDateString("en", { day: "numeric", month: "short", timeZone: "UTC" });
}

// ---- rendering ----

function fillSelect(select, dim, rows, current) {
  const options = [["", "All"]];
  for (const r of rows)
    options.push([String(r[dim]), `${label(dim, r[dim])} (${numberFormat.format(r.n)})`]);
  if (current !== "" && !rows.some((r) => String(r[dim]) === current))
    options.push([current, `${label(dim, current)} (0)`]);
  select.replaceChildren(...options.map(([value, text]) => {
    const o = document.createElement("option");
    o.value = value;
    o.textContent = text;
    return o;
  }));
  select.value = current;
}

function crosshairPlugin() {
  return {
    id: "crosshair",
    afterDatasetsDraw(chart) {
      const active = chart.tooltip?.getActiveElements?.() ?? [];
      if (!active.length)
        return;
      const { ctx, chartArea } = chart;
      const x = active[0].element.x;
      ctx.save();
      ctx.strokeStyle = cssVar("--axis");
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, chartArea.top);
      ctx.lineTo(x, chartArea.bottom);
      ctx.stroke();
      ctx.restore();
    },
  };
}

function commonScales() {
  const grid = cssVar("--grid");
  const muted = cssVar("--text-muted");
  return {
    x: { grid: { display: false }, border: { color: cssVar("--axis") }, ticks: { color: muted, maxRotation: 0, autoSkipPadding: 16 } },
    y: { beginAtZero: true, grid: { color: grid }, border: { display: false }, ticks: { color: muted, precision: 0 } },
  };
}

function tooltipStyle() {
  return {
    backgroundColor: cssVar("--surface-1"),
    titleColor: cssVar("--text-secondary"),
    bodyColor: cssVar("--text-primary"),
    borderColor: cssVar("--border"),
    borderWidth: 1,
    padding: 10,
    boxPadding: 4,
    usePointStyle: true,
  };
}

function renderTimeline(bucket, state, rows) {
  const keys = timeBuckets(bucket, state, rows);
  const split = state.split;
  let series;
  if (!split)
    series = [{ name: "Downloads", color: cssVar("--series-1"), counts: new Map(rows.map((r) => [r[bucket], r.n])) }];
  else {
    const totals = new Map();
    for (const r of rows)
      totals.set(r[split], (totals.get(r[split]) ?? 0) + r.n);
    const ranked = [...totals].sort((a, b) => b[1] - a[1]);
    const top = ranked.slice(0, MAX_SPLIT_SERIES).map(([v]) => v);
    const topSet = new Set(top);
    const slots = assignSlots(split, top);
    series = top.map((v) => ({ name: label(split, v), color: cssVar(`--series-${slots.get(v)}`), counts: new Map() }));
    const other = { name: "Other", color: cssVar("--other"), counts: new Map() };
    for (const r of rows) {
      const s = topSet.has(r[split]) ? series[top.indexOf(r[split])] : other;
      s.counts.set(r[bucket], (s.counts.get(r[bucket]) ?? 0) + r.n);
    }
    if (other.counts.size)
      series.push(other);
  }

  const single = series.length === 1;
  const datasets = series.map((s) => ({
    label: s.name,
    data: keys.map((k) => s.counts.get(k) ?? 0),
    borderColor: s.color,
    backgroundColor: single ? s.color + "1a" : s.color,
    pointBackgroundColor: s.color,
    pointBorderColor: s.color,
    pointHoverBorderColor: cssVar("--surface-1"),
    fill: single ? "origin" : false,
    borderWidth: 2,
    tension: 0,
    pointRadius: keys.length === 1 ? 4 : 0,
    pointHoverRadius: 5,
    pointHoverBorderWidth: 2,
  }));

  document.getElementById("timeline-title").textContent =
    `Downloads per ${bucket}` + (split ? `, split by ${form.elements.split.selectedOptions[0].textContent}` : "");

  if (timelineChart)
    timelineChart.destroy();
  timelineChart = new Chart(document.getElementById("timeline"), {
    type: "line",
    data: { labels: keys.map((k) => formatBucket(bucket, k)), datasets },
    options: {
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "index", intersect: false },
      scales: commonScales(),
      plugins: {
        legend: {
          display: !single,
          position: "top",
          align: "start",
          labels: { color: cssVar("--text-secondary"), usePointStyle: true, pointStyle: "line", boxWidth: 16 },
        },
        tooltip: {
          ...tooltipStyle(),
          itemSort: (a, b) => b.raw - a.raw,
          callbacks: {
            title: (items) => (bucket === "week" ? "Week of " : "") + items[0].label,
            label: (item) => ` ${numberFormat.format(item.raw)}  ${item.dataset.label}`,
            labelPointStyle: () => ({ pointStyle: "line", rotation: 0 }),
          },
        },
      },
    },
    plugins: [crosshairPlugin()],
  });

  const table = document.getElementById("timeline-table");
  const head = document.createElement("tr");
  for (const text of [bucket[0].toUpperCase() + bucket.slice(1), ...series.map((s) => s.name)]) {
    const th = document.createElement("th");
    th.textContent = text;
    if (head.children.length)
      th.className = "num";
    head.append(th);
  }
  const body = document.createElement("tbody");
  for (let i = keys.length - 1; i >= 0; i--) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.textContent = keys[i];
    tr.append(td);
    for (const s of series) {
      const c = document.createElement("td");
      c.className = "num";
      c.textContent = numberFormat.format(s.counts.get(keys[i]) ?? 0);
      tr.append(c);
    }
    body.append(tr);
  }
  const thead = document.createElement("thead");
  thead.append(head);
  table.replaceChildren(thead, body);
}

function drillDown(dim, value) {
  if (!FILTER_DIMS.includes(dim))
    return;
  const select = form.elements[dim];
  if (![...select.options].some((o) => o.value === String(value))) {
    const o = document.createElement("option");
    o.value = String(value);
    o.textContent = label(dim, value);
    select.append(o);
  }
  select.value = String(value);
  if (dim === "project")
    form.elements.version.disabled = false;
  const next = { project: "version", version: "country", country: "os" }[dim];
  if (next)
    form.elements.group.value = next;
  update();
}

function renderGroup(dim, rows) {
  const total = rows.reduce((sum, r) => sum + r.n, 0);
  const shown = rows.slice(0, MAX_BARS);
  const box = document.getElementById("bars-box");
  box.style.height = `${Math.max(60, shown.length * 30 + 30)}px`;

  if (barsChart)
    barsChart.destroy();
  barsChart = new Chart(document.getElementById("bars"), {
    type: "bar",
    data: {
      labels: shown.map((r) => label(dim, r[dim])),
      datasets: [{
        data: shown.map((r) => r.n),
        backgroundColor: cssVar("--series-1"),
        hoverBackgroundColor: cssVar("--series-1") + "cc",
        maxBarThickness: 24,
        borderRadius: 4,
        borderSkipped: "start",
      }],
    },
    options: {
      indexAxis: "y",
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "nearest", axis: "y", intersect: false },
      onClick: (_, elements) => {
        if (elements.length)
          drillDown(dim, shown[elements[0].index][dim]);
      },
      onHover: (event, elements) => {
        event.native.target.style.cursor = elements.length ? "pointer" : "default";
      },
      scales: (() => {
        const s = commonScales();
        return {
          x: { ...s.y, position: "top" },
          y: { grid: { display: false }, border: { color: cssVar("--axis") }, ticks: { color: cssVar("--text-secondary"), autoSkip: false } },
        };
      })(),
      plugins: {
        legend: { display: false },
        tooltip: {
          ...tooltipStyle(),
          usePointStyle: false,
          displayColors: false,
          callbacks: {
            label: (item) => `${numberFormat.format(item.raw)} downloads (${total ? ((item.raw / total) * 100).toFixed(1) : 0}%)`,
          },
        },
      },
    },
  });

  const table = document.getElementById("group-table");
  const thead = document.createElement("thead");
  const head = document.createElement("tr");
  for (const [text, cls] of [[form.elements.group.selectedOptions[0].textContent, ""], ["Downloads", "num"], ["Share", "num"]]) {
    const th = document.createElement("th");
    th.textContent = text;
    th.className = cls;
    head.append(th);
  }
  thead.append(head);
  const body = document.createElement("tbody");
  const clickable = FILTER_DIMS.includes(dim);
  for (const r of rows) {
    const tr = document.createElement("tr");
    if (clickable) {
      tr.className = "clickable";
      tr.addEventListener("click", () => drillDown(dim, r[dim]));
    }
    for (const [text, cls] of [[label(dim, r[dim]), ""], [numberFormat.format(r.n), "num"], [`${total ? ((r.n / total) * 100).toFixed(1) : 0}%`, "num"]]) {
      const td = document.createElement("td");
      td.textContent = text;
      td.className = cls;
      tr.append(td);
    }
    body.append(tr);
  }
  table.replaceChildren(thead, body);
  if (!rows.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.className = "empty";
    td.textContent = "No downloads match these filters.";
    tr.append(td);
    body.append(tr);
  }
}

async function update() {
  const state = stateFromForm();
  writeState(state);

  const seq = ++renderSeq;
  app.classList.add("loading");
  const errorBox = document.getElementById("error");
  try {
    const bucket = bucketFor(state);
    const timeParams = baseParams(state);
    timeParams.set("group", bucket);
    if (state.split)
      timeParams.set("group2", state.split);
    const groupParams = baseParams(state);
    groupParams.set("group", state.group);

    const optionRequests = FILTER_DIMS.map((d) => {
      const p = baseParams(state, { withFilters: false });
      if (d === "version") {
        if (!state.project)
          return Promise.resolve([]);
        p.set("project", state.project);
      }
      p.set("group", d);
      return api(p);
    });
    const [timeRows, groupRows, ...optionRows] = await Promise.all([api(timeParams), api(groupParams), ...optionRequests]);
    if (seq !== renderSeq)
      return;

    FILTER_DIMS.forEach((d, i) => fillSelect(form.elements[d], d, optionRows[i], state[d]));
    const total = timeRows.reduce((sum, r) => sum + r.n, 0);
    document.getElementById("total").textContent = numberFormat.format(total);
    document.getElementById("total-label").textContent = state.range === "custom"
      ? `downloads from ${formatDate(state.from)} to ${formatDate(state.to)}`
      : `downloads ${form.elements.range.selectedOptions[0].textContent.toLowerCase()}`;
    lastRender = { bucket, state, timeRows, groupRows };
    renderTimeline(bucket, state, timeRows);
    renderGroup(state.group, groupRows);
    errorBox.hidden = true;
  }
  catch (e) {
    errorBox.textContent = `Could not load statistics: ${e.message}`;
    errorBox.hidden = false;
  }
  finally {
    if (seq === renderSeq)
      app.classList.remove("loading");
  }
}

function applyState(state) {
  for (const k of ["range", "group", "split", "from", "to"])
    form.elements[k].value = state[k];
  for (const d of FILTER_DIMS) {
    const select = form.elements[d];
    if (state[d] && ![...select.options].some((o) => o.value === state[d])) {
      const o = document.createElement("option");
      o.value = state[d];
      o.textContent = label(d, state[d]);
      select.append(o);
    }
    select.value = state[d];
  }
  form.elements.dep.checked = state.dep === "1";
  form.elements.ci.checked = state.ci === "1";
}

form.addEventListener("change", (e) => {
  if (e.target.name === "project")
    form.elements.version.value = "";
  if (e.target.name === "range" && e.target.value === "custom" && lastRender) {
    const span = dateSpan(lastRender.state);
    form.elements.from.value = span.from ?? "";
    form.elements.to.value = span.to;
  }
  update();
});
form.elements.group.addEventListener("change", update);
form.elements.split.addEventListener("change", update);
document.getElementById("reset").addEventListener("click", () => {
  applyState({ ...DEFAULTS, ...Object.fromEntries(FILTER_DIMS.map((d) => [d, ""])) });
  update();
});

// The web font usually arrives after the first render, and canvas text does not reflow by itself.
document.fonts.ready.then(() => {
  if (lastRender) {
    renderTimeline(lastRender.bucket, lastRender.state, lastRender.timeRows);
    renderGroup(lastRender.state.group, lastRender.groupRows);
  }
});

applyState(readState());
update();
