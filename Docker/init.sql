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

INSERT INTO job_subscriptions (customer_id, industries, job_info, created_at)
VALUES (
    '0ce32985-7fda-4c20-ad62-3ac0a9b23231',
    '[
        "消費性電子產品製造業",
        "電腦軟體服務業",
        "人力仲介代徵",
        "其他電子零組件相關業",
        "多媒體相關業",
        "廣告行銷公關業"
      ]
    '::jsonb, -- 假設行業
    '[
        "Java",
        "VueJS",
        "HTML",
        "jQuery",
        "Node.js"
      ]'::jsonb, -- 假設職位信息
    NOW() -- 當前時間
);

SELECT * FROM job_subscriptions;