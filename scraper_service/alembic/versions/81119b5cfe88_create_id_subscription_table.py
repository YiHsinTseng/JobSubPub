"""create_id_subscription_table

Revision ID: 81119b5cfe88
Revises: 68064fbc2c92
Create Date: 2025-03-09 21:51:44.160632

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = '81119b5cfe88'
down_revision: Union[str, None] = '68064fbc2c92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_content = """
    CREATE TABLE IF NOT EXISTS job_id_subscriptions (
        id SERIAL PRIMARY KEY,             -- 自增主键
        user_id UUID NOT NULL UNIQUE,  -- 顾客 ID，使用 UUID 格式，并要求唯一
        job_ids JSONB,         -- 行业栏位，使用 JSONB 格式
        company_names JSONB,           -- 关键字栏位，使用 JSONB 格式
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间，默认为当前时间
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 创建时间，默认为当前时间
    );
    """

    if sql_content:
        # 如果有提供 SQL 內容，執行該內容
        op.execute(sql_content)
    else:
        # 如果沒有 SQL 內容，則根據檔案位置執行 SQL 文件
        sql_file_path = os.path.join(
            os.path.dirname(__file__),  # 當前文件目錄
            '../../../postgres_db/create_id_subs.sql'  # 相對於該目錄的路徑
        )

        # 解析為絕對路徑
        sql_file_path = os.path.abspath(sql_file_path)

        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        # 執行從 SQL 文件讀取的腳本
        op.execute(sql_script)


def downgrade() -> None:
    """Downgrade schema."""
    sql_content = """
    DROP TABLE IF EXISTS job_id_subscriptions;
    """
    
    # 執行刪除表格的 SQL
    op.execute(sql_content)
