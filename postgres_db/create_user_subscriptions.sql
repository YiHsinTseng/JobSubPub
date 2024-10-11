CREATE TABLE IF NOT EXISTS users (
  user_id UUID PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS  subscriptions_jobs (
    user_id UUID,
    job_id VARCHAR(255),
    PRIMARY KEY (user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE IF NOT EXISTS subscriptions_companies (
    user_id UUID,
    company_name VARCHAR(255),
    PRIMARY KEY (user_id, company_name),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
