CREATE TABLE job_tags (
  id SERIAL PRIMARY KEY,
  tag_name VARCHAR(50) UNIQUE NOT NULL
);
CREATE TABLE subscriptions_jobs_tags (
  user_id UUID,
  -- 外鍵，指向subscriptions_jobs表
  job_id VARCHAR(255),
  -- 外鍵，指向subscriptions_jobs表
  tag_id INT,
  PRIMARY KEY (job_id, tag_id, user_id),
  -- 複合主鍵：job_id, tag_id 和 user_id 的組合
  FOREIGN KEY (user_id, job_id) REFERENCES subscriptions_jobs(user_id, job_id) -- 外鍵，指向 subscriptions_jobs 表的 user_id
  ON DELETE CASCADE,
  -- 要加上以免被禁止刪除
  FOREIGN KEY (tag_id) REFERENCES job_tags(id) -- 外鍵，指向 tags 表的 id
);