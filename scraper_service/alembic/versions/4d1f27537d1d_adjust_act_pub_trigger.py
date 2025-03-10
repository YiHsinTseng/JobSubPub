"""Adjust act pub trigger

Revision ID: 4d1f27537d1d
Revises: 63b04a7a418c
Create Date: 2025-03-10 06:41:11.296901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = '4d1f27537d1d'
down_revision: Union[str, None] = '63b04a7a418c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS job_update_trigger ON jobs;")
    op.execute("DROP TRIGGER IF EXISTS company_update_trigger ON jobs;")
    op.execute("DROP FUNCTION IF EXISTS notify_job_update;")
    op.execute("DROP FUNCTION IF EXISTS notify_company_add;")
    
    sql_content = """
    -- Drop existing triggers if they exist
    -- DROP TRIGGER IF EXISTS job_update_trigger ON jobs;
    -- DROP TRIGGER IF EXISTS company_update_trigger ON jobs;
    -- Function to handle job updates
    CREATE OR REPLACE FUNCTION notify_job_update() RETURNS trigger AS $$
    DECLARE changed_fields jsonb := '{}'::jsonb;
    -- JSON object to record changed fields
    BEGIN -- Ensure job_id exists in job_id_channel table
    IF NOT EXISTS (
        SELECT 1
        FROM job_id_channel
        WHERE job_id = NEW.job_id
    ) THEN RETURN NEW;
    -- If job_id doesn't exist, skip further processing
    END IF;
    -- Check each field for changes and update changed_fields
    IF NEW.job_title IS DISTINCT
    FROM OLD.job_title THEN changed_fields := jsonb_set(
            changed_fields,
            '{job_title}',
            to_jsonb(NEW.job_title)
        );
    END IF;
    IF NEW.job_exp IS DISTINCT
    FROM OLD.job_exp THEN changed_fields := jsonb_set(
            changed_fields,
            '{job_exp}',
            to_jsonb(NEW.job_exp)
        );
    -- 更新 job_exp_year 為數字 (例如 3)
    NEW.job_exp_year := CASE
        WHEN NEW.job_exp = '經歷不拘' THEN 0
        WHEN NEW.job_exp = '不拘' THEN 0
        ELSE CAST(
            REGEXP_REPLACE(NEW.job_exp, '[^0-9]', '', 'g') AS INTEGER
        )
    END;
    -- 紀錄 job_exp 變更到 changed_fields (以 "X年以上" 格式儲存)
    changed_fields := jsonb_set(
        changed_fields,
        '{job_exp}',
        to_jsonb(
            CASE
                WHEN NEW.job_exp = '經歷不拘' THEN '經歷不拘'
                WHEN NEW.job_exp = '不拘' THEN 0
                ELSE NEW.job_exp
            END
        )
    );
    END IF;
    IF NEW.job_desc IS DISTINCT
    FROM OLD.job_desc THEN changed_fields := jsonb_set(
            changed_fields,
            '{job_desc}',
            to_jsonb(left(NEW.job_desc, 1000))
        );
    END IF;
    IF NEW.job_info IS DISTINCT
    FROM OLD.job_info THEN changed_fields := jsonb_set(
            changed_fields,
            '{job_info}',
            to_jsonb(NEW.job_info)
        );
    END IF;
    IF NEW.job_condition IS DISTINCT
    FROM OLD.job_condition THEN changed_fields := jsonb_set(
            changed_fields,
            '{job_condition}',
            to_jsonb(NEW.job_condition)
        );
    END IF;
    IF NEW.job_salary IS DISTINCT
    FROM OLD.job_salary THEN changed_fields := jsonb_set(
            changed_fields,
            '{job_salary}',
            to_jsonb(NEW.job_salary)
        );
    END IF;
    IF NEW.people IS DISTINCT
    FROM OLD.people THEN changed_fields := jsonb_set(changed_fields, '{people}', to_jsonb(NEW.people));
    END IF;
    IF NEW.place IS DISTINCT
    FROM OLD.place THEN changed_fields := jsonb_set(changed_fields, '{place}', to_jsonb(NEW.place));
    END IF;
    IF NEW.update_date IS DISTINCT
    FROM OLD.update_date THEN changed_fields := jsonb_set(
            changed_fields,
            '{update_date}',
            to_jsonb(NEW.update_date)
        );
    END IF;
    -- 在插入推播通知前，將 job_desc 進行處理
    NEW.job_desc := trim(
        both ' '
        FROM NEW.job_desc
    );
    -- 去除前後空格
    IF length(NEW.job_desc) > 1000 THEN NEW.job_desc := left(NEW.job_desc, 1000);
    -- 如果超過1000字符，則截斷
    END IF;
    -- Send notification if there are changes
    IF changed_fields != '{}'::jsonb THEN PERFORM pg_notify(
        'job_id_channel',
        json_build_object(
            'job_title',
            NEW.job_title,
            'job_id',
            NEW.job_id,
            'changed_fields',
            changed_fields,
            'data',
            row_to_json(NEW)
        )::text
    );
    -- Insert into trigger log
    INSERT INTO trigger_log (event_type, event_data)
    VALUES (
            'job_update_notification',
            json_build_object(
                'job_title',
                NEW.job_title,
                'job_id',
                NEW.job_id,
                'changed_fields',
                changed_fields,
                'data',
                row_to_json(NEW)
            )
        );
    END IF;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    -- Function to handle company updates
    CREATE OR REPLACE FUNCTION notify_company_add() RETURNS trigger AS $$ BEGIN -- Send notification if company_name exists in company_name_channel table
        IF EXISTS (
            SELECT 1
            FROM company_name_channel
            WHERE company_name = NEW.company_name
        ) THEN PERFORM pg_notify(
            'company_name_channel',
            json_build_object(
                'company_name',
                NEW.company_name,
                'job_id',
                NEW.job_id,
                'changed_fields',
                json_build_object(
                    'job_title',
                    NEW.job_title
                ),
                'data',
                row_to_json(NEW)
            )::text
        );
    -- Insert into trigger log
    INSERT INTO trigger_log (event_type, event_data)
    VALUES (
            'company_name_notification',
            json_build_object(
                'company_name',
                NEW.company_name,
                'job_id',
                NEW.job_id,
                'changed_fields',
                json_build_object(
                    'job_title',
                    NEW.job_title
                ),
                'data',
                row_to_json(NEW)
            )
        );
    END IF;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    -- Create triggers
    CREATE OR REPLACE TRIGGER job_update_trigger
    AFTER
    UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION notify_job_update();
    CREATE OR REPLACE TRIGGER company_update_trigger
    AFTER
    INSERT ON jobs FOR EACH ROW EXECUTE FUNCTION notify_company_add();
    """

    if sql_content:
        # 如果有提供 SQL 內容，執行該內容
        op.execute(sql_content)
    else:
        # 如果沒有 SQL 內容，則根據檔案位置執行 SQL 文件
        sql_file_path = os.path.join(
            os.path.dirname(__file__),  # 當前文件目錄
            '../../../postgres_db/create_act_pub_trigger.sql'  # 相對於該目錄的路徑
        )

        # 解析為絕對路徑
        sql_file_path = os.path.abspath(sql_file_path)   
             
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        # 執行從 SQL 文件讀取的腳本
        op.execute(sql_script)



def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS job_update_trigger ON jobs;")
    op.execute("DROP TRIGGER IF EXISTS company_update_trigger ON jobs;")
    op.execute("DROP FUNCTION IF EXISTS notify_job_update;")
    op.execute("DROP FUNCTION IF EXISTS notify_company_add;")
    
    sql_content="""
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
    """
  
    op.execute(sql_content)
   
