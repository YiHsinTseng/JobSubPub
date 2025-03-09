"""create_trigger_and_log

Revision ID: b2e1747d5986
Revises: 478edef09330
Create Date: 2025-03-09 21:57:32.277707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = 'b2e1747d5986'
down_revision: Union[str, None] = '478edef09330'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_contents = [
        """
        CREATE TABLE IF NOT EXISTS trigger_log (
            id SERIAL PRIMARY KEY,
            event_type TEXT,
            event_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
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
    ]

    if sql_contents:
        # 如果有提供 SQL 內容，執行該內容
        for sql_content in sql_contents:
            op.execute(sql_content)
    else:
        # SQL 檔案的路徑
        sql_files = [
            '../../../postgres_db/create_trigger_log.sql',
            '../../../postgres_db/create_act_pub_trigger.sql'
        ]  

        # 讀取並執行所有 SQL 文件
        for sql_file in sql_files:
            # 計算相對路徑的絕對路徑
            sql_file_path = os.path.join(os.path.dirname(__file__), sql_file)
            sql_file_path = os.path.abspath(sql_file_path)

            # 讀取 SQL 腳本
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_script = file.read()

            # 執行 SQL 腳本
            op.execute(sql_script)


def downgrade() -> None:
    """Downgrade schema."""
    # 刪除觸發器
    op.execute("DROP TRIGGER IF EXISTS job_update_trigger ON jobs;")
    op.execute("DROP TRIGGER IF EXISTS company_update_trigger ON jobs;")
    
    # 刪除函數
    op.execute("DROP FUNCTION IF EXISTS notify_job_update;")
    op.execute("DROP FUNCTION IF EXISTS notify_company_add;")
    
    # 刪除表格
    op.execute("DROP TABLE IF EXISTS trigger_log;")
