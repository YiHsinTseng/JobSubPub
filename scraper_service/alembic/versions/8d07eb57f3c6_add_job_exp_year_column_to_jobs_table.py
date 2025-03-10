"""Add job_exp_year column to jobs table

Revision ID: 8d07eb57f3c6
Revises: b2e1747d5986
Create Date: 2025-03-10 04:57:58.317176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision: str = '8d07eb57f3c6'
down_revision: Union[str, None] = 'b2e1747d5986'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 定義 job_exp 的轉換規則
job_exp_mapping = {
    "經歷不拘": 0,
    **{f"{i}年以上": i for i in range(1, 11)}  # 自動生成 1~10 年
}

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('jobs', sa.Column('job_exp_year', sa.Integer(), nullable=True))
    # 更新 job_exp_year 欄位的值
    bind = op.get_bind()
    session = Session(bind=bind)
    # 使用 sa.text() 來包裝原始 SQL 查詢
    jobs = session.execute(sa.text("SELECT job_id, job_exp FROM jobs")).fetchall()
    
    for job in jobs:
        # 使用欄位名稱來訪問元組，增強可讀性
        job_id = job.job_id
        job_exp = job.job_exp
        
        # 取得對應的經驗年數
        job_exp_year = job_exp_mapping.get(job_exp)
        
        # 如果有對應的經驗年數，則更新
        if job_exp_year is not None:
            session.execute(
                sa.text("""
                    UPDATE jobs 
                    SET job_exp_year = :job_exp_year 
                    WHERE job_id = :job_id
                """),
                {'job_exp_year': job_exp_year, 'job_id': job_id}
            )
    # 提交更新
    session.commit()

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('jobs', 'job_exp_year')

