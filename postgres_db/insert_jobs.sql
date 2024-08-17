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
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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