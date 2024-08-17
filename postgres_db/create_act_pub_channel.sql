CREATE TABLE IF NOT EXISTS job_id_channel (
  job_id INTEGER PRIMARY KEY,
	user_ids JSONB
);

-- Drop TABLE job_id_channel

CREATE TABLE IF NOT EXISTS company_name_channel (
  company_name TEXT PRIMARY KEY,
	user_ids JSONB
);

-- Drop TABLE company_name_channel

-- select * from job_id_channel;
select * from company_name_channel;