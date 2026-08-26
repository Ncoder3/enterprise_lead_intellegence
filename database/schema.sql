CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- =========================================================
-- SOURCES
-- =========================================================

CREATE TABLE IF NOT EXISTS sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_sources_name UNIQUE (source_name)
);


-- =========================================================
-- COMPANIES
-- =========================================================

CREATE TABLE IF NOT EXISTS companies (
    company_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    company_name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    industry VARCHAR(150),
    country VARCHAR(100),
    employee_count INTEGER,
    company_size VARCHAR(50),
    website TEXT,

    source_id UUID REFERENCES sources(source_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_employee_count
        CHECK (employee_count IS NULL OR employee_count >= 0)
);


-- =========================================================
-- PEOPLE
-- =========================================================

CREATE TABLE IF NOT EXISTS people (
    person_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    company_id UUID REFERENCES companies(company_id)
        ON DELETE SET NULL,

    first_name VARCHAR(100),
    last_name VARCHAR(100),
    job_title VARCHAR(200),
    linkedin_url TEXT,

    source_id UUID REFERENCES sources(source_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================================================
-- EMAILS
-- =========================================================

CREATE TABLE IF NOT EXISTS emails (
    email_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    person_id UUID NOT NULL REFERENCES people(person_id)
        ON DELETE CASCADE,

    email VARCHAR(320) NOT NULL,

    email_type VARCHAR(50),
    verification_status VARCHAR(50),
    verification_score NUMERIC(5,4),
    verified_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_person_email
        UNIQUE (person_id, email),

    CONSTRAINT chk_verification_score
        CHECK (
            verification_score IS NULL
            OR (
                verification_score >= 0
                AND verification_score <= 1
            )
        )
);


-- =========================================================
-- SCRAPE RUNS
-- =========================================================

CREATE TABLE IF NOT EXISTS scrape_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_id UUID REFERENCES sources(source_id),

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,

    status VARCHAR(30) NOT NULL DEFAULT 'running',

    pages_attempted INTEGER NOT NULL DEFAULT 0,
    pages_succeeded INTEGER NOT NULL DEFAULT 0,

    records_extracted INTEGER NOT NULL DEFAULT 0,
    records_failed INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================================================
-- SCRAPE PAGES
-- =========================================================

CREATE TABLE IF NOT EXISTS scrape_pages (
    page_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    run_id UUID NOT NULL
        REFERENCES scrape_runs(run_id)
        ON DELETE CASCADE,

    page_number INTEGER NOT NULL,

    page_url TEXT NOT NULL,

    status VARCHAR(30) NOT NULL,

    records_extracted INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================================================
-- LEADS (Phase 2H Complete Schema)
-- =========================================================

CREATE TABLE IF NOT EXISTS leads (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_id UUID REFERENCES sources(source_id),
    run_id UUID REFERENCES scrape_runs(run_id),

    -- Contact Core Data
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    job_title VARCHAR(255),
    email VARCHAR(320) NOT NULL,

    -- Company Core Data
    company_name VARCHAR(255),
    domain VARCHAR(255),
    industry VARCHAR(255),
    country VARCHAR(100),
    employee_count INTEGER,

    -- Identity Matching (Phase 2H)
    normalized_full_name VARCHAR(255),
    identity_key VARCHAR(500),

    -- Email Validation Metadata
    email_status VARCHAR(50) NOT NULL DEFAULT 'unverified',
    email_validation_status VARCHAR(50),
    email_validation_reason TEXT,
    email_mx_valid BOOLEAN,
    email_is_free_provider BOOLEAN,
    email_is_disposable BOOLEAN,
    email_validated_at TIMESTAMPTZ,

    -- Data Quality Scoring (Phase 2H)
    data_quality_score INTEGER DEFAULT 0,
    lead_quality_score NUMERIC(5,2),
    lead_quality VARCHAR(50),
    quality_reasons TEXT[],

    -- Deduplication Tracking (Phase 2H)
    duplicate_status VARCHAR(30) DEFAULT 'unique',
    duplicate_reason TEXT,
    duplicate_checked_at TIMESTAMPTZ,

    -- Timestamps
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Phase 2j fo rthe observbility of each step

CREATE TABLE IF NOT EXISTS run_metrics (
    run_id UUID PRIMARY KEY REFERENCES scrape_runs(run_id) ON DELETE CASCADE,
    records_discovered INT DEFAULT 0,
    records_normalized INT DEFAULT 0,
    records_valid INT DEFAULT 0,
    records_invalid INT DEFAULT 0,
    high_quality_leads INT DEFAULT 0,
    medium_quality_leads INT DEFAULT 0,
    low_quality_leads INT DEFAULT 0,
    duplicates_detected INT DEFAULT 0,
    records_merged INT DEFAULT 0,
    records_reviewed INT DEFAULT 0,
    records_inserted INT DEFAULT 0,
    records_updated INT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_companies_domain
    ON companies(domain);

CREATE INDEX IF NOT EXISTS idx_companies_industry
    ON companies(industry);

CREATE INDEX IF NOT EXISTS idx_people_company
    ON people(company_id);

CREATE INDEX IF NOT EXISTS idx_people_job_title
    ON people(job_title);

CREATE INDEX IF NOT EXISTS idx_emails_email
    ON emails(email);

CREATE INDEX IF NOT EXISTS idx_emails_status
    ON emails(verification_status);

CREATE INDEX IF NOT EXISTS idx_scrape_runs_source
    ON scrape_runs(source_id);

CREATE INDEX IF NOT EXISTS idx_scrape_runs_status
    ON scrape_runs(status);

CREATE INDEX IF NOT EXISTS idx_scrape_pages_run
    ON scrape_pages(run_id);

-- Phase 2H Lead Bank Indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_email_unique ON leads (LOWER(email));

CREATE INDEX IF NOT EXISTS idx_leads_identity_key ON leads(identity_key);

CREATE INDEX IF NOT EXISTS idx_leads_domain ON leads(domain);

CREATE INDEX IF NOT EXISTS idx_leads_quality ON leads(data_quality_score);