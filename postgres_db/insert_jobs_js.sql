INSERT INTO jobs (
    job_title, 
    company_name, 
    industry, 
    job_exp, 
    job_desc, 
    job_info, 
    job_condition, 
    job_salary, 
    people, 
    place, 
    update_date, 
    record_time, 
    source, 
    keywords, 
    job_link
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
)
ON CONFLICT (job_link) DO UPDATE
SET
    job_title = EXCLUDED.job_title,
    company_name = EXCLUDED.company_name,
    industry = EXCLUDED.industry,
    job_exp = EXCLUDED.job_exp,
    job_desc = EXCLUDED.job_desc,
    job_info = EXCLUDED.job_info,
    job_condition = EXCLUDED.job_condition,
    job_salary = EXCLUDED.job_salary,
    people = EXCLUDED.people,
    place = EXCLUDED.place,
    update_date = EXCLUDED.update_date,
    record_time = EXCLUDED.record_time,
    source = EXCLUDED.source,
    keywords = EXCLUDED.keywords
;
