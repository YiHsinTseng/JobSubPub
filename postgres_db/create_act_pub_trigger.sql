-- Drop existing triggers if they exist
-- DROP TRIGGER IF EXISTS job_update_trigger ON jobs;
-- DROP TRIGGER IF EXISTS company_update_trigger ON jobs;

-- Function to handle job updates
CREATE OR REPLACE FUNCTION notify_job_update() RETURNS trigger AS $$
DECLARE
    changed_fields jsonb := '{}'::jsonb;  -- JSON object to record changed fields
BEGIN
    -- Ensure job_id exists in job_id_channel table
    IF NOT EXISTS (SELECT 1 FROM job_id_channel WHERE job_id = NEW.job_id) THEN
        RETURN NEW;  -- If job_id doesn't exist, skip further processing
    END IF;

    -- Check each field for changes and update changed_fields
    IF NEW.job_title IS DISTINCT FROM OLD.job_title THEN
        changed_fields := jsonb_set(changed_fields, '{job_title}', to_jsonb(NEW.job_title));
    END IF;

    IF NEW.job_exp IS DISTINCT FROM OLD.job_exp THEN
        changed_fields := jsonb_set(changed_fields, '{job_exp}', to_jsonb(NEW.job_exp));
    END IF;

    IF NEW.job_desc IS DISTINCT FROM OLD.job_desc THEN
        changed_fields := jsonb_set(changed_fields, '{job_desc}', to_jsonb(NEW.job_desc));
    END IF;

    IF NEW.job_info IS DISTINCT FROM OLD.job_info THEN
        changed_fields := jsonb_set(changed_fields, '{job_info}', to_jsonb(NEW.job_info));
    END IF;

    IF NEW.job_condition IS DISTINCT FROM OLD.job_condition THEN
        changed_fields := jsonb_set(changed_fields, '{job_condition}', to_jsonb(NEW.job_condition));
    END IF;

    IF NEW.job_salary IS DISTINCT FROM OLD.job_salary THEN
        changed_fields := jsonb_set(changed_fields, '{job_salary}', to_jsonb(NEW.job_salary));
    END IF;

    IF NEW.people IS DISTINCT FROM OLD.people THEN
        changed_fields := jsonb_set(changed_fields, '{people}', to_jsonb(NEW.people));
    END IF;

    IF NEW.place IS DISTINCT FROM OLD.place THEN
        changed_fields := jsonb_set(changed_fields, '{place}', to_jsonb(NEW.place));
    END IF;

    IF NEW.update_date IS DISTINCT FROM OLD.update_date THEN
        changed_fields := jsonb_set(changed_fields, '{update_date}', to_jsonb(NEW.update_date));
    END IF;

    -- Send notification if there are changes
    IF changed_fields != '{}'::jsonb THEN
        PERFORM pg_notify('job_id_channel', json_build_object(
            'job_title', NEW.job_title,
            'job_id', NEW.job_id,
            'changed_fields', changed_fields,
			'data', row_to_json(NEW)
        )::text);

        -- Insert into trigger log
        INSERT INTO trigger_log (event_type, event_data)
        VALUES ('job_update_notification', json_build_object(
            'job_title', NEW.job_title,
            'job_id', NEW.job_id,
            'changed_fields', changed_fields,
			'data', row_to_json(NEW)
        ));
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to handle company updates
CREATE OR REPLACE FUNCTION notify_company_add() RETURNS trigger AS $$
BEGIN
    -- Send notification if company_name exists in company_name_channel table
    IF EXISTS (SELECT 1 FROM company_name_channel WHERE company_name = NEW.company_name) THEN
        PERFORM pg_notify('company_name_channel', json_build_object(
            'company_name', NEW.company_name,
			'job_id', NEW.job_id,
            'changed_fields', json_build_object(
                'job_title', NEW.job_title
            ),
			'data', row_to_json(NEW)
        )::text);
        
        -- Insert into trigger log
        INSERT INTO trigger_log (event_type, event_data)
        VALUES ('company_name_notification', json_build_object(
            'company_name', NEW.company_name,
			'job_id', NEW.job_id,
            'changed_fields', json_build_object(
                'job_title', NEW.job_title
            ),
			'data', row_to_json(NEW)
        ));
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE OR REPLACE TRIGGER job_update_trigger
AFTER UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION notify_job_update();

CREATE OR REPLACE TRIGGER company_update_trigger
AFTER INSERT ON jobs
FOR EACH ROW
EXECUTE FUNCTION notify_company_add();
