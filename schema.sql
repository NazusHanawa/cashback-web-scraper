PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT
);

CREATE TABLE IF NOT EXISTS platforms (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT,
    cashback_value_path TEXT,
    cashback_description_path TEXT
);

CREATE TABLE IF NOT EXISTS partnerships (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    platform_id INTEGER NOT NULL,
    url TEXT NOT NULL,

    UNIQUE(store_id, platform_id),
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cashbacks (
    id INTEGER PRIMARY KEY,
    partnership_id INTEGER NOT NULL,
    value REAL NOT NULL CHECK (value >= 0),
    description TEXT,
    
    date_start TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    date_end TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (partnership_id) REFERENCES partnerships(id) ON DELETE CASCADE
);