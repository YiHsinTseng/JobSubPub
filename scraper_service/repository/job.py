"""
操作整個DB的所有table的schema變化，而非專屬於scrape
由於爬蟲伺服器寫入較多，因此讓其管理整個DB
但其管理交由alembic，創建專案所需要的所有資料表
雖然缺少ORM操作的便利性，但比較易懂，容易直接測試SQL
但考慮交給migration紀錄變更
"""

from database.db_handler import PostgresHandler


class JobRepository:
    def __init__(self):
        self.db_handler = PostgresHandler()

    """
    jobs只先在參數驗證是list(在腳本層已經由JobModel來驗證)
    把dict value的驗證交由資料庫層
    """

    def insert_jobs_into_postgres(self, jobs: list[dict]):
        try:
            # with open("../postgres_db/insert_jobs.sql", 'r', encoding='utf-8') as file:
            #     insert_jobs_sql = file.read()
            insert_jobs_sql = """
            INSERT INTO jobs (
                job_title,
                company_name,
                industry,
                job_exp,
                job_exp_year,
                job_desc,
                job_info,
                job_condition,
                job_salary,
                people,
                place,
                update_date,
                record_time,
                source,
                keywords,
                job_link
            )
            VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
            ) ON CONFLICT (job_link) DO
            UPDATE
            SET job_title = EXCLUDED.job_title,
                company_name = EXCLUDED.company_name,
                industry = EXCLUDED.industry,
                job_exp = EXCLUDED.job_exp,
                job_exp_year = EXCLUDED.job_exp_year,
                job_desc = EXCLUDED.job_desc,
                job_info = EXCLUDED.job_info,
                job_condition = EXCLUDED.job_condition,
                job_salary = EXCLUDED.job_salary,
                people = EXCLUDED.people,
                place = EXCLUDED.place,
                update_date = EXCLUDED.update_date,
                record_time = EXCLUDED.record_time,
                source = EXCLUDED.source,
                keywords = EXCLUDED.keywords;
            """
            with self.db_handler.get_cursor() as cur:
                for job in jobs:
                    values = tuple(job.values())
                    cur.execute(insert_jobs_sql, values)
                self.db_handler.commit()
            # print(f"成功將 {len(jobs)} 個職位信息插入到 PostgreSQL 表格中")
        except Exception as e:
            print(f"插入數據庫時出錯: {e}")
            self.db_handler.rollback()
