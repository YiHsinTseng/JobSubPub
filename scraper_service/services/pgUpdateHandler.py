
""" 
操作整個DB的所有table的schema變化，而非專屬於scrape
由於爬蟲伺服器寫入較多，因此讓其管理整個DB
但其管理交由alembic，創建專案所需要的所有資料表
雖然缺少ORM操作的便利性，但比較易懂，容易直接測試SQL
但考慮交給migration紀錄變更
"""
import os
import psycopg2

# import json
from dotenv import load_dotenv
load_dotenv()

class PostgresHandler:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        self.cur = self.conn.cursor()
    """
    jobs只先在參數驗證是list(在腳本層已經由JobModel來驗證)
    把dict value的驗證交由資料庫層
    """
    def insert_jobs_into_postgres(self, jobs: list[dict]):
        try:
            with open("../postgres_db/insert_jobs.sql", 'r', encoding='utf-8') as file:
                insert_jobs_sql = file.read()
            with self.conn.cursor() as cur:
                for job in jobs:
                    values = tuple(job.values())
                    cur.execute(insert_jobs_sql, values)
                self.conn.commit()
            print(f'成功將 {len(jobs)} 個職位信息插入到 PostgreSQL 表格中')
        except Exception as e:
          print(f'插入數據庫時出錯: {e}')
          self.conn.rollback()
