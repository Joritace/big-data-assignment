PRAGMA foreign_keys = OFF;

-- Main patent table
CREATE TABLE IF NOT EXISTS patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    filing_date TEXT,
    abstract TEXT,
    year INTEGER
);

-- Inventor lookup table
CREATE TABLE IF NOT EXISTS inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    gender_code TEXT,
    country TEXT,
    location_id TEXT
);

-- Company / assignee lookup table
CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT,
    location_id TEXT
);

-- Relationship table connecting patents to inventors and companies
CREATE TABLE IF NOT EXISTS relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT
);

-- WIPO technology classification table
CREATE TABLE IF NOT EXISTS wipo_technology (
    patent_id TEXT,
    wipo_sector_title TEXT,
    wipo_field_title TEXT
);

-- CPC technical classification table
CREATE TABLE IF NOT EXISTS cpc_at_issue (
    patent_id TEXT,
    cpc_section TEXT,
    cpc_class TEXT,
    cpc_subclass TEXT,
    cpc_group TEXT,
    cpc_type TEXT,
    action_date TEXT
);

-- CPC title lookup table
CREATE TABLE IF NOT EXISTS cpc_title (
    cpc_section TEXT,
    cpc_class TEXT,
    cpc_subclass TEXT,
    cpc_group TEXT,
    title TEXT
);

-- Patent figures table used for complexity analysis
CREATE TABLE IF NOT EXISTS figures (
    patent_id TEXT,
    num_figures INTEGER,
    num_sheets INTEGER
);

-- PCT / international filing table
CREATE TABLE IF NOT EXISTS pct_data (
    patent_id TEXT,
    filed_country TEXT
);

-- Government interest table
CREATE TABLE IF NOT EXISTS gov_interest (
    patent_id TEXT,
    gov_interest_text TEXT
);

-- Government organization table
CREATE TABLE IF NOT EXISTS gov_interest_org (
    patent_id TEXT,
    fedagency_name TEXT,
    level_one TEXT
);

-- Government contracts table
CREATE TABLE IF NOT EXISTS gov_interest_contracts (
    patent_id TEXT,
    contract_number TEXT
);

-- Citation influence table
CREATE TABLE IF NOT EXISTS patent_citation_influence (
    patent_id TEXT,
    total_citations INTEGER
);

-- References made by each citing patent
CREATE TABLE IF NOT EXISTS citing_patent_references (
    patent_id TEXT,
    total_references_made INTEGER
);

-- Citation category summary table
CREATE TABLE IF NOT EXISTS citation_category_counts (
    citation_category TEXT,
    total_citations INTEGER
);

-- indexes to optimize query performance

CREATE INDEX IF NOT EXISTS idx_patents_patent_id ON patents(patent_id);
CREATE INDEX IF NOT EXISTS idx_patents_year ON patents(year);

CREATE INDEX IF NOT EXISTS idx_inventors_inventor_id ON inventors(inventor_id);
CREATE INDEX IF NOT EXISTS idx_inventors_country ON inventors(country);
CREATE INDEX IF NOT EXISTS idx_inventors_name ON inventors(name);

CREATE INDEX IF NOT EXISTS idx_companies_company_id ON companies(company_id);
CREATE INDEX IF NOT EXISTS idx_companies_country ON companies(country);
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);

CREATE INDEX IF NOT EXISTS idx_relationships_patent_id ON relationships(patent_id);
CREATE INDEX IF NOT EXISTS idx_relationships_inventor_id ON relationships(inventor_id);
CREATE INDEX IF NOT EXISTS idx_relationships_company_id ON relationships(company_id);

CREATE INDEX IF NOT EXISTS idx_wipo_patent_id ON wipo_technology(patent_id);
CREATE INDEX IF NOT EXISTS idx_wipo_sector_title ON wipo_technology(wipo_sector_title);
CREATE INDEX IF NOT EXISTS idx_wipo_field_title ON wipo_technology(wipo_field_title);

CREATE INDEX IF NOT EXISTS idx_cpc_patent_id ON cpc_at_issue(patent_id);
CREATE INDEX IF NOT EXISTS idx_cpc_section ON cpc_at_issue(cpc_section);
CREATE INDEX IF NOT EXISTS idx_cpc_class ON cpc_at_issue(cpc_class);
CREATE INDEX IF NOT EXISTS idx_cpc_subclass ON cpc_at_issue(cpc_subclass);
CREATE INDEX IF NOT EXISTS idx_cpc_group ON cpc_at_issue(cpc_group);

CREATE INDEX IF NOT EXISTS idx_cpc_title_subclass ON cpc_title(cpc_subclass);
CREATE INDEX IF NOT EXISTS idx_cpc_title_group ON cpc_title(cpc_group);
CREATE INDEX IF NOT EXISTS idx_cpc_title_class ON cpc_title(cpc_class);

CREATE INDEX IF NOT EXISTS idx_figures_patent_id ON figures(patent_id);

CREATE INDEX IF NOT EXISTS idx_pct_patent_id ON pct_data(patent_id);
CREATE INDEX IF NOT EXISTS idx_pct_filed_country ON pct_data(filed_country);

CREATE INDEX IF NOT EXISTS idx_gov_interest_patent_id ON gov_interest(patent_id);
CREATE INDEX IF NOT EXISTS idx_gov_contracts_patent_id ON gov_interest_contracts(patent_id);
CREATE INDEX IF NOT EXISTS idx_gov_org_patent_id ON gov_interest_org(patent_id);
CREATE INDEX IF NOT EXISTS idx_gov_org_agency ON gov_interest_org(fedagency_name);
CREATE INDEX IF NOT EXISTS idx_gov_org_level_one ON gov_interest_org(level_one);

CREATE INDEX IF NOT EXISTS idx_citation_influence_patent_id ON patent_citation_influence(patent_id);
CREATE INDEX IF NOT EXISTS idx_citation_influence_total ON patent_citation_influence(total_citations);
CREATE INDEX IF NOT EXISTS idx_citing_refs_patent_id ON citing_patent_references(patent_id);
CREATE INDEX IF NOT EXISTS idx_citation_category ON citation_category_counts(citation_category);
