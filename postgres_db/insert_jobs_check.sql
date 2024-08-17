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
WHERE (
    jobs.job_title IS DISTINCT FROM EXCLUDED.job_title OR
    jobs.company_name IS DISTINCT FROM EXCLUDED.company_name OR
    jobs.industry IS DISTINCT FROM EXCLUDED.industry OR
    jobs.job_exp IS DISTINCT FROM EXCLUDED.job_exp OR
    jobs.job_desc IS DISTINCT FROM EXCLUDED.job_desc OR
    jobs.job_info IS DISTINCT FROM EXCLUDED.job_info OR
    jobs.job_condition IS DISTINCT FROM EXCLUDED.job_condition OR
    jobs.job_salary IS DISTINCT FROM EXCLUDED.job_salary OR
    jobs.people IS DISTINCT FROM EXCLUDED.people OR
    jobs.place IS DISTINCT FROM EXCLUDED.place OR
    jobs.update_date IS DISTINCT FROM EXCLUDED.update_date OR
    jobs.record_time IS DISTINCT FROM EXCLUDED.record_time OR
    jobs.source IS DISTINCT FROM EXCLUDED.source OR
    jobs.keywords IS DISTINCT FROM EXCLUDED.keywords
);