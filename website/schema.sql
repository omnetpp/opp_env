CREATE TABLE IF NOT EXISTS downloads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL DEFAULT (date('now')),
  project TEXT NOT NULL,
  version TEXT NOT NULL,
  dependency INTEGER,
  country TEXT,
  os TEXT,
  arch TEXT,
  opp_env_version TEXT,
  ci INTEGER,
  store_backed INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS downloads_date ON downloads (date);
