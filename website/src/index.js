import { handleStatsApi, handleStatsCsv } from "./stats.js";

const MAX_REPORT_BYTES = 1024;

// The values end up on the dashboard, so only plausible tokens are stored.
const TOKEN = /^[A-Za-z0-9_.+-]{1,40}$/;
const REPORT_FIELDS = {
  project: { required: true, pattern: /^[a-z0-9_]{1,40}$/ },
  version: { required: true, pattern: TOKEN },
  dependency: { boolean: true },
  os: { pattern: /^[a-z]{1,16}$/ },
  arch: { pattern: /^[A-Za-z0-9_]{1,16}$/ },
  ci: { boolean: true },
  opp_env_version: { pattern: TOKEN },
  store_backed: { boolean: true },
};

export function parseReport(body) {
  let report;
  try {
    report = JSON.parse(body);
  }
  catch {
    return { error: "body is not valid JSON" };
  }
  if (report === null || typeof report !== "object" || Array.isArray(report))
    return { error: "body must be a JSON object" };
  const row = {};
  for (const [key, value] of Object.entries(report)) {
    // A newer opp_env may send fields this worker does not know yet; its downloads should still count.
    if (!Object.hasOwn(REPORT_FIELDS, key))
      continue;
    const field = REPORT_FIELDS[key];
    const valid = field.boolean ? typeof value === "boolean" : typeof value === "string" && field.pattern.test(value);
    // An odd host value (e.g. an unusual OS name) should not cost the whole count.
    if (!valid && field.required)
      return { error: `invalid value for '${key}'` };
    row[key] = !valid ? null : field.boolean ? Number(value) : value;
  }
  for (const [key, field] of Object.entries(REPORT_FIELDS)) {
    if (field.required && !(key in row))
      return { error: `'${key}' is required` };
  }
  return { row };
}

// Returns null once the body exceeds maxBytes, so an oversized or endless body is never fully buffered.
async function readBodyWithLimit(request, maxBytes) {
  if (!request.body)
    return "";
  const reader = request.body.getReader();
  const chunks = [];
  let size = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done)
      break;
    size += value.byteLength;
    if (size > maxBytes) {
      await reader.cancel();
      return null;
    }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return new TextDecoder().decode(bytes);
}

function text(body, status, headers = {}) {
  return new Response(body, {
    status,
    headers: { "content-type": "text/plain; charset=utf-8", ...headers },
  });
}

async function handleReport(request, env, ctx) {
  if (request.method !== "POST")
    return text("Method not allowed\n", 405, { allow: "POST" });
  // Before any parsing, so a flood stays cheap. Keyed on the IP, which is only used for this counter.
  const { success } = await env.REPORT_LIMITER.limit({ key: request.headers.get("cf-connecting-ip") ?? "" });
  if (!success)
    return text("Too many reports\n", 429, { "retry-after": "60" });
  if (!(request.headers.get("content-type") || "").startsWith("application/json"))
    return text("Content-Type must be application/json\n", 415);
  if (Number(request.headers.get("content-length") || 0) > MAX_REPORT_BYTES)
    return text("Report too large\n", 413);
  const body = await readBodyWithLimit(request, MAX_REPORT_BYTES);
  if (body === null)
    return text("Report too large\n", 413);

  const { row, error } = parseReport(body);
  if (error)
    return text(`Bad report: ${error}\n`, 400);

  ctx.waitUntil(
    env.DB.prepare(
      "INSERT INTO downloads (project, version, dependency, country, os, arch, opp_env_version, ci, store_backed) " +
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
      // opp_env releases without read-only store packages do not send store_backed: those are regular installs
      .bind(row.project, row.version, row.dependency ?? null, request.cf?.country ?? null,
            row.os ?? null, row.arch ?? null, row.opp_env_version ?? null, row.ci ?? null, row.store_backed ?? 0)
      .run()
      .catch((e) => console.error("recording download failed:", e))
  );
  return new Response(null, { status: 204 });
}

export default {
  async fetch(request, env, ctx) {
    const { pathname } = new URL(request.url);
    if (pathname === "/report")
      return handleReport(request, env, ctx);
    if (request.method !== "GET" && request.method !== "HEAD")
      return text("Method not allowed\n", 405, { allow: "GET, HEAD" });
    if (pathname === "/stats/api")
      return handleStatsApi(request, env, ctx);
    if (pathname === "/stats/csv")
      return handleStatsCsv(request, env);
    return text("Not found\n", 404);
  },
};
