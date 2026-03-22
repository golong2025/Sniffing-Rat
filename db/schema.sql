CREATE TABLE IF NOT EXISTS traffic_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_ip TEXT,
    url TEXT,
    title TEXT,
    platform TEXT,
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER,
    content_type TEXT,
    query_params TEXT
);

CREATE TABLE IF NOT EXISTS media_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    traffic_id INTEGER,
    url TEXT,
    local_path TEXT,
    media_type TEXT, -- image / video
    thumbnail_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(traffic_id) REFERENCES traffic_logs(id)
);

CREATE TABLE IF NOT EXISTS credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    traffic_id INTEGER,
    platform TEXT,
    username TEXT,
    password TEXT,
    raw_data TEXT,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(traffic_id) REFERENCES traffic_logs(id)
);
