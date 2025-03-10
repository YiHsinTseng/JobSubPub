"""create subscriptions_job_tags table

Revision ID: 2634e03b1dba
Revises: 4d1f27537d1d
Create Date: 2025-03-10 07:54:32.017272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = '2634e03b1dba'
down_revision: Union[str, None] = '4d1f27537d1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_content = """
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
    """

    if sql_content:
        # 如果有提供 SQL 內容，執行該內容
        op.execute(sql_content)
    else:
        # 如果沒有 SQL 內容，則根據檔案位置執行 SQL 文件
        sql_file_path = os.path.join(
            os.path.dirname(__file__),  # 當前文件目錄
            '../../../postgres_db/create_subs_jobs_tags.sql'  # 相對於該目錄的路徑
        )

        # 解析為絕對路徑
        sql_file_path = os.path.abspath(sql_file_path)   
             
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        # 執行從 SQL 文件讀取的腳本
        op.execute(sql_script)


def downgrade() -> None:
    """Downgrade schema."""
     # 回滾操作：刪除創建的表格
    sql_content = """
    DROP TABLE IF EXISTS job_tags;
    DROP TABLE IF EXISTS subscriptions_jobs_tags;
    """
    
    # 執行刪除表格的 SQL
    op.execute(sql_content)

