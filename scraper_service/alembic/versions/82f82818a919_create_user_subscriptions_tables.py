"""create_user_subscriptions_tables

Revision ID: 82f82818a919
Revises: 81119b5cfe88
Create Date: 2025-03-09 21:53:35.796902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = '82f82818a919'
down_revision: Union[str, None] = '81119b5cfe88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_content = """
    CREATE TABLE IF NOT EXISTS users (
        user_id UUID PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS  subscriptions_jobs (
        user_id UUID,
        job_id VARCHAR(255),
        PRIMARY KEY (user_id, job_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );


    CREATE TABLE IF NOT EXISTS subscriptions_companies (
        user_id UUID,
        company_name VARCHAR(255),
        PRIMARY KEY (user_id, company_name),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """

    if sql_content:
        # 如果有提供 SQL 內容，執行該內容
        op.execute(sql_content)
    else:
        # 如果沒有 SQL 內容，則根據檔案位置執行 SQL 文件
        sql_file_path = os.path.join(
            os.path.dirname(__file__),  # 當前文件目錄
            '../../../postgres_db/create_user_subscriptions.sql'  # 相對於該目錄的路徑
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
    DROP TABLE IF EXISTS subscriptions_companies;
    DROP TABLE IF EXISTS subscriptions_jobs;
    DROP TABLE IF EXISTS users;
    """
    
    # 執行刪除表格的 SQL
    op.execute(sql_content)
