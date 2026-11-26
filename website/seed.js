// Generates fake download rows for developing the dashboard against the local D1:
//   node seed.js > .wrangler/seed.sql && npx wrangler d1 execute oppenv-stats --local --file .wrangler/seed.sql
const COUNT = Number(process.argv[2] ?? 3000);
const DAYS = 400;

const models = [
  ["inet", ["4.5.4", "4.5.2", "4.4.1", "3.8.3"], 30, ["omnetpp"]],
  ["simu5g", ["1.3.0", "1.2.2"], 10, ["omnetpp", "inet"]],
  ["veins", ["5.3.1", "5.2"], 8, ["omnetpp"]],
  ["omnetpp", ["6.2.0", "6.1.0", "6.0.3", "5.7.1"], 25, []],
  ["simulte", ["1.2.0"], 2, ["omnetpp", "inet"]],
  ["wifidirect_allinone", ["3.4"], 1, []],
];
const depVersions = { omnetpp: "6.1.0", inet: "4.5.4" };
const countries = [["DE", 20], ["US", 12], ["CN", 12], ["IN", 10], ["HU", 6], ["IT", 6], ["BR", 5], ["FR", 5], ["GB", 4], ["KR", 4], ["JP", 3], ["TR", 3], ["ES", 3], ["IR", 3], ["PK", 2]];
const platforms = [[["linux", "x86_64"], 60], [["wsl", "x86_64"], 18], [["macos", "arm64"], 15], [["macos", "x86_64"], 3], [["linux", "aarch64"], 4]];
const oppEnvVersions = [["0.36.3.261123", 60], ["0.36.2.261110", 30], ["0.35.0.260420", 10]];

function pick(weighted) {
  const total = weighted.reduce((s, [, w]) => s + w, 0);
  let r = Math.random() * total;
  for (const [v, w] of weighted)
    if ((r -= w) < 0)
      return v;
  return weighted[0][0];
}
const q = (v) => (v === null ? "NULL" : typeof v === "number" ? String(v) : `'${String(v).replace(/'/g, "''")}'`);

const lines = ["DELETE FROM downloads;"];
for (let i = 0; i < COUNT; i++) {
  const age = Math.floor(Math.pow(Math.random(), 1.6) * DAYS);
  const date = new Date(Date.now() - age * 86400000).toISOString().slice(0, 10);
  const country = pick(countries);
  const [os, arch] = pick(platforms);
  const ci = Math.random() < 0.2 ? 1 : 0;
  const ver = pick(oppEnvVersions);
  const [project, versions, , deps] = pick(models.map((m) => [m, m[2]]));
  const version = versions[Math.floor(Math.pow(Math.random(), 1.5) * versions.length)];
  for (const [p, v, dep] of [...deps.map((d) => [d, depVersions[d], 1]), [project, version, 0]])
    lines.push(`INSERT INTO downloads (date, project, version, dependency, country, os, arch, opp_env_version, ci) VALUES (${q(date)}, ${q(p)}, ${q(v)}, ${dep}, ${q(country)}, ${q(os)}, ${q(arch)}, ${q(ver)}, ${ci});`);
}
console.log(lines.join("\n"));
