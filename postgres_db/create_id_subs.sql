CREATE TABLE IF NOT EXISTS job_id_subscriptions (
    id SERIAL PRIMARY KEY,             -- 自增主键
    customer_id UUID NOT NULL UNIQUE,  -- 顾客 ID，使用 UUID 格式，并要求唯一
    job_ids JSONB,         -- 行业栏位，使用 JSONB 格式
    company_names JSONB,           -- 关键字栏位，使用 JSONB 格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间，默认为当前时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 创建时间，默认为当前时间
);