CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- =========================================================
-- SOURCES
-- =========================================================

CREATE TABLE sources (
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

CREATE TABLE companies (
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

CREATE TABLE people (
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

CREATE TABLE emails (
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

CREATE TABLE scrape_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_id UUID REFERENCES sources(source_id),

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,

    status VARCHAR(30) NOT NULL DEFAULT 'running',

    records_found INTEGER NOT NULL DEFAULT 0,
    records_processed INTEGER NOT NULL DEFAULT 0,
    records_failed INTEGER NOT NULL DEFAULT 0,

    error_message TEXT
);


-- =========================================================
-- LEADS
-- =========================================================

CREATE TABLE leads (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    person_id UUID NOT NULL REFERENCES people(person_id)
        ON DELETE CASCADE,

    lead_status VARCHAR(50) NOT NULL DEFAULT 'new',

    icp_score NUMERIC(5,2),

    lead_tier VARCHAR(20),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_icp_score
        CHECK (
            icp_score IS NULL
            OR (
                icp_score >= 0
                AND icp_score <= 100
            )
        )
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX idx_companies_domain
    ON companies(domain);

CREATE INDEX idx_companies_industry
    ON companies(industry);

CREATE INDEX idx_people_company
    ON people(company_id);

CREATE INDEX idx_people_job_title
    ON people(job_title);

CREATE INDEX idx_emails_email
    ON emails(email);

CREATE INDEX idx_emails_status
    ON emails(verification_status);

CREATE INDEX idx_scrape_runs_source
    ON scrape_runs(source_id);

CREATE INDEX idx_scrape_runs_status
    ON scrape_runs(status);

CREATE INDEX idx_leads_person
    ON leads(person_id);

CREATE INDEX idx_leads_status
    ON leads(lead_status);

CREATE INDEX idx_leads_icp_score
    ON leads(icp_score);