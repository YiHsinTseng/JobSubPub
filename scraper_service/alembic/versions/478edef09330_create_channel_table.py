"""create_channel_table

Revision ID: 478edef09330
Revises: 82f82818a919
Create Date: 2025-03-09 21:55:31.022190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '478edef09330'
down_revision: Union[str, None] = '82f82818a919'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_content = """
    CREATE TABLE IF NOT EXISTS job_id_channel (
    job_id INTEGER PRIMARY KEY,
        user_ids JSONB
    );

    -- Drop TABLE job_id_channel

    CREATE TABLE IF NOT EXISTS company_name_channel (
    company_name TEXT PRIMARY KEY,
        user_ids JSONB
    );
    """

    if sql_content:
        # 如果有提供 SQL 內容，執行該內容
        op.execute(sql_content)
    else:
        # 如果沒有 SQL 內容，則根據檔案位置執行 SQL 文件
        sql_file_path = os.path.join(
            os.path.dirname(__file__),  # 當前文件目錄
            '../../../postgres_db/create_act_pub_channel.sql'  # 相對於該目錄的路徑
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
    DROP TABLE IF EXISTS company_name_channel;
    DROP TABLE IF EXISTS job_id_channel;
    """
    
    # 執行刪除表格的 SQL
    op.execute(sql_content)
