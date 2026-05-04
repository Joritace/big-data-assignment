-- schema.sql

CREATE TABLE IF NOT EXISTS patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    filing_date TEXT,
    year INTEGER,
    abstract TEXT
);

CREATE TABLE IF NOT EXISTS inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT,
    location_id TEXT
);

CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT,
    location_id TEXT
);

CREATE TABLE IF NOT EXISTS relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT
);