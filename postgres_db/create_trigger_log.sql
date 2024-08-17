CREATE TABLE IF NOT EXISTS trigger_log (
    id SERIAL PRIMARY KEY,
    event_type TEXT,
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from trigger_log;


-- Drop Table trigger_log;