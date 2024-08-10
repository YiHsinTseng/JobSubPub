import psycopg2
import json

class PostgresHandler:
    def __init__(self):
        # PostgreSQL 連接設置
        self.conn = psycopg2.connect(
            host="localhost",
            database="jobs",
            user="test",
            password="test"
        )
        self.cur = self.conn.cursor()
        #  創建表格（如果不存在）
        self.create_table()
    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id SERIAL PRIMARY KEY,
            job_title character varying(255),
            company_name character varying(255),
            industry character varying(255),
            job_exp character varying(50),
            job_desc TEXT,
            job_info JSONB,
            job_condition TEXT,
            job_salary character varying(255),
            people character varying(50),
            place character varying(255),
            update_date DATE,
            record_time TIMESTAMP,
            source character varying(50),
            keywords character varying(255),
            job_link character varying(1024) UNIQUE
        );
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_table_query)
                self.conn.commit()
            print("表格 'jobs' 已成功創建或已存在。")
        except Exception as e:
            print(f'創建表格時出錯: {e}')
            self.conn.rollback()
    def insert_jobs_into_postgres(self, jobs):
        try:
            with self.conn.cursor() as cur:
                ##基本上jobs內的dict在前面即符合JobModel(可以考慮驗證驗證) 
                for job in jobs:
                    ##其實JobModel應該要跟PG欄位名稱一樣，這裡並沒有做到
                    ##如果欄位衝突的話要怎樣解決，目前是後面直接取代前面
                    cur.execute("""
                        INSERT INTO jobs (
                            job_title, 
                            company_name, 
                            industry, 
                            job_exp, 
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
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (job_link) DO UPDATE
                        SET
                            job_title = EXCLUDED.job_title,
                            company_name = EXCLUDED.company_name,
                            industry = EXCLUDED.industry,
                            job_exp = EXCLUDED.job_exp,
                            job_desc = EXCLUDED.job_desc,
                            job_info = EXCLUDED.job_info,
                            job_condition = EXCLUDED.job_condition,
                            job_salary = EXCLUDED.job_salary,
                            people = EXCLUDED.people,
                            place = EXCLUDED.place,
                            update_date = EXCLUDED.update_date,
                            record_time = EXCLUDED.record_time,
                            source = EXCLUDED.source,
                            keywords = EXCLUDED.keywords
                    """, (
                        job['title'],  
                        job['company_name'],  
                        job['industry'],  
                        job['experience'],  
                        job['description'],  
                        json.dumps(job['requirements']),  
                        job['additional_conditions'],  
                        job['salary'],  
                        job['applicants'],  
                        job['location'],  
                        job['update_date'],  
                        job['record_time'],  
                        job['source'],  
                        job['keywords'],
                        job['url']  
                    ))
                self.conn.commit()
            print(f'成功將 {len(jobs)} 個職位信息插入到 PostgreSQL 表格中')
        except Exception as e:
          print(f'插入數據庫時出錯: {e}')
          self.conn.rollback()
