// SQL expressions per dimension. Only these keys are accepted from the client, and
// values are always bound parameters, so the browser can never inject SQL.
const DIMENSIONS = {
  project: "COALESCE(project, '')",
  version: "COALESCE(version, '')",
  country: "COALESCE(country, '')",
  os: "COALESCE(os, '')",
  arch: "COALESCE(arch, '')",
  opp_env_version: "COALESCE(opp_env_version, '')",
  ci: "COALESCE(ci, 0)",
  dependency: "COALESCE(dependency, 0)",
  day: "date",
  week: "date(date, '-' || ((CAST(strftime('%w', date) AS INTEGER) + 6) % 7) || ' days')",
  month: "substr(date, 1, 7)",
};

const TIME_DIMENSIONS = new Set(["day", "week", "month"]);
const NUMERIC_DIMENSIONS = new Set(["ci", "dependency"]);
const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const CACHE_SECONDS = 900;

function json(body, status, cacheControl = "no-store") {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": cacheControl },
  });
}

// The stats are only for signed-in users, so shared caches must not keep them, and the browser must
// not add its own delay on top of the worker's cache (which only requests passing Cloudflare Access reach).
function privately(response) {
  const copy = new Response(response.body, response);
  copy.headers.set("cache-control", "private, no-cache");
  return copy;
}

function badRequest(message) {
  return json({ error: message }, 400);
}

export function buildQuery(params) {
  const groups = [];
  const where = [];
  const binds = [];

  for (const [key, value] of params) {
    if (key === "group" || key === "group2") {
      if (!Object.hasOwn(DIMENSIONS, value))
        return { error: `unknown dimension '${value}' in '${key}'` };
      groups.push(value);
    }
    else if (key === "from" || key === "to") {
      if (!DATE_PATTERN.test(value))
        return { error: `'${key}' must be YYYY-MM-DD` };
      where.push(key === "from" ? "date >= ?" : "date <= ?");
      binds.push(value);
    }
    else if (Object.hasOwn(DIMENSIONS, key) && !TIME_DIMENSIONS.has(key)) {
      if (NUMERIC_DIMENSIONS.has(key) && value !== "0" && value !== "1")
        return { error: `'${key}' must be 0 or 1` };
      where.push(`${DIMENSIONS[key]} = ?`);
      binds.push(NUMERIC_DIMENSIONS.has(key) ? Number(value) : value);
    }
    else
      return { error: `unknown parameter '${key}'` };
  }

  if (!params.has("group"))
    return { error: "'group' is required" };
  if (params.getAll("group").length > 1 || params.getAll("group2").length > 1)
    return { error: "'group' and 'group2' may only be given once" };
  if (groups.length === 2 && groups[0] === groups[1])
    return { error: "'group' and 'group2' must differ" };

  const select = groups.map((g) => `${DIMENSIONS[g]} AS ${g}`).join(", ");
  const orderBy = TIME_DIMENSIONS.has(groups[0]) ? groups[0] : "n DESC";
  const sql = `SELECT ${select}, count(*) AS n FROM downloads` +
    (where.length ? ` WHERE ${where.join(" AND ")}` : "") +
    // By the expressions, not the aliases: SQLite resolves a GROUP BY name to the column first, so NULL and
    // 0 (or '') would come back as two groups with the same key.
    ` GROUP BY ${groups.map((g) => DIMENSIONS[g]).join(", ")} ORDER BY ${orderBy}`;
  return { sql, binds };
}

export async function handleStatsApi(request, env, ctx) {
  const url = new URL(request.url);
  const params = new URLSearchParams([...url.searchParams].sort(([a], [b]) => a.localeCompare(b)));
  const query = buildQuery(params);
  if (query.error)
    return badRequest(query.error);

  url.search = params.toString();
  const cacheKey = new Request(url.toString());
  const cache = caches.default;
  const cached = await cache.match(cacheKey);
  if (cached)
    return privately(cached);

  let results;
  try {
    ({ results } = await env.DB.prepare(query.sql).bind(...query.binds).all());
  }
  catch (e) {
    console.error("stats query failed:", e);
    return json({ error: "query failed" }, 500);
  }
  const response = json({ rows: results }, 200, `public, max-age=${CACHE_SECONDS}`);
  ctx.waitUntil(cache.put(cacheKey, response.clone()));
  return privately(response);
}

const CSV_COLUMNS = ["date", "project", "version", "dependency", "country", "os", "arch", "opp_env_version", "ci", "store_backed"];
const CSV_CHUNK_ROWS = 10000;

function csvField(value) {
  if (value === null || value === undefined)
    return "";
  const s = String(value);
  return /[",\r\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

// Streams the whole table in keyset-paginated chunks, so the export does not have to fit in memory.
export function handleStatsCsv(request, env) {
  const encoder = new TextEncoder();
  const query = env.DB.prepare(`SELECT id, ${CSV_COLUMNS.join(", ")} FROM downloads WHERE id > ? ORDER BY id LIMIT ?`);
  let lastId = 0;
  const body = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(CSV_COLUMNS.join(",") + "\r\n"));
    },
    async pull(controller) {
      try {
        const { results } = await query.bind(lastId, CSV_CHUNK_ROWS).all();
        if (results.length) {
          controller.enqueue(encoder.encode(
            results.map((r) => CSV_COLUMNS.map((c) => csvField(r[c])).join(",") + "\r\n").join("")));
          lastId = results[results.length - 1].id;
        }
        if (results.length < CSV_CHUNK_ROWS)
          controller.close();
      }
      catch (e) {
        console.error("csv export failed:", e);
        controller.error(e);
      }
    },
  });
  const date = new Date().toISOString().slice(0, 10);
  return new Response(body, {
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": `attachment; filename="omnetpp-downloads-${date}.csv"`,
      "cache-control": "no-store",
    },
  });
}
