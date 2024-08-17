CREATE TABLE IF NOT EXISTS job_subscriptions (
    id SERIAL PRIMARY KEY,             
    customer_id UUID NOT NULL UNIQUE, 
    industries JSONB NOT NULL,         
    job_info JSONB NOT NULL,          
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);