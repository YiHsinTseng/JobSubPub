CREATE TABLE IF NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,
    job_title character varying(255),
    company_name character varying(255),
    industry character varying(255),
    job_exp character varying(50),
    job_desc TEXT,
    job_info JSONB,
    job_condition TEXT,
    job_salary character varying(255),
    people character varying(50),
    place character varying(255),
    update_date DATE,
    record_time TIMESTAMP,
    source character varying(50),
    keywords character varying(255),
    job_link character varying(1024) UNIQUE
);

CREATE TABLE IF NOT EXISTS job_subscriptions (
    id SERIAL PRIMARY KEY,
    customer_id UUID NOT NULL UNIQUE,
    industries JSONB NOT NULL,
    job_info JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
