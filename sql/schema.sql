CREATE TABLE IF NOT EXISTS anime (
    mal_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    title_english TEXT,
    title_japanese TEXT,
    type_ TEXT,
    source_ TEXT,
    episodes INTEGER,
    status_ TEXT,
    airing BOOLEAN,
    aired_from DATE,
    aired_to DATE,
    duration TEXT,
    rating TEXT,
    score NUMERIC(4,2) CHECK (score IS NULL OR (score >= 0 AND score <= 10)),
    scored_by INTEGER,
    rank_ INTEGER,
    popularity INTEGER,
    members INTEGER,
    favorites INTEGER,
    synopsis TEXT,
    year_ INTEGER,
    season TEXT,
    studios TEXT,
    genres TEXT,
    themes TEXT,
    demographics TEXT
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    timestamp_inizio TIMESTAMP NOT NULL,
    timestamp_fine TIMESTAMP NOT NULL,
    durata_secondi NUMERIC(10,1),
    record_estratti INTEGER DEFAULT 0,
    record_trasformati INTEGER DEFAULT 0,
    record_caricati INTEGER DEFAULT 0,
    stato TEXT NOT NULL CHECK (stato IN ('SUCCESSO', 'FALLITO')),
    errore TEXT
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_timestamp
    ON pipeline_runs (timestamp_inizio DESC);