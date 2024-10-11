import os
import psycopg2
import json
from dotenv import load_dotenv ##poetry add python-dotenv

# 加載 .env 文件中的環境變量
load_dotenv()

class PostgresHandler:
    def __init__(self):
        # PostgreSQL 連接設置
        # self.conn = psycopg2.connect(
        #     host="localhost",
        #     database="jobs",
        #     user="test",
        #     password="test"
        # )
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        self.cur = self.conn.cursor()
        #  創建表格（如果不存在）
        self.create_table()
        self.create_subscription_table()
        self.create_id_subscription_table()
        self.create_channel_table()
        self.create_user_subscriptions_tables()
        self.create_trigger_and_log()
    def create_table(self):
        with open("../postgres_db/create_jobs.sql", 'r', encoding='utf-8') as file:
            create_jobs_sql = file.read()
        try:   
            with self.conn.cursor() as cur:
                cur.execute(create_jobs_sql)
                self.conn.commit()
            print("表格 'jobs' 已成功創建或已存在。")
        except Exception as e:
            print(f'創建表格時出錯: {e}')
            self.conn.rollback()
   
    def create_subscription_table(self):
        with open("../postgres_db/create_jobs.sql", 'r', encoding='utf-8') as file:
            create_job_subs_sql = file.read()
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_job_subs_sql)
                self.conn.commit()
            print("表格 'job_subscriptions' 已成功創建或已存在。")
        except Exception as e:
            print(f'創建表格時出錯: {e}')
            self.conn.rollback()
    def create_id_subscription_table(self):
            with open("../postgres_db/create_id_subs.sql", 'r', encoding='utf-8') as file:
                create_id_subs_sql = file.read()
            try:
                with self.conn.cursor() as cur:
                    cur.execute(create_id_subs_sql)
                    self.conn.commit()
                print("表格 'job_id_subscriptions' 已成功創建或已存在。")
            except Exception as e:
                print(f'創建表格時出錯: {e}')
                self.conn.rollback()
    def create_channel_table(self):
        with open("../postgres_db/create_act_pub_channel.sql", 'r', encoding='utf-8') as file:
            create_act_pub_channel_sql = file.read()
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_act_pub_channel_sql)
                self.conn.commit()
            print("表格 'act_pub_channel_tables' 已成功創建或已存在。")
        except Exception as e:
            print(f'創建表格時出錯: {e}')
            self.conn.rollback()
    def create_user_subscriptions_tables(self):
        with open("../postgres_db/create_user_subscriptions.sql", 'r', encoding='utf-8') as file:
            create_user_subscriptions_sql = file.read()
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_user_subscriptions_sql)
                self.conn.commit()
            print("表格 'user_subscriptions_tables' 已成功創建或已存在。")
        except Exception as e:
            print(f'創建表格時出錯: {e}')
            self.conn.rollback()
    def create_trigger_and_log(self):
            with open("../postgres_db/create_trigger_log.sql", 'r', encoding='utf-8') as file:
                create_trigger_log_sql = file.read()   
            with open("../postgres_db/create_act_pub_trigger.sql", 'r', encoding='utf-8') as file:
                create_trigger_sql = file.read()
            try:
                with self.conn.cursor() as cur:
                    cur.execute(create_trigger_log_sql)
                    self.conn.commit()
                print("表格 'trigger_log' 已成功創建或已存在。")
                with self.conn.cursor() as cur:
                    cur.execute(create_trigger_sql)
                    self.conn.commit()
                print("表格 'act_pub_trigger' 已成功創建或已存在。")
            except Exception as e:
                print(f'創建表格時出錯: {e}')
                self.conn.rollback()
    def insert_jobs_into_postgres(self, jobs):
        try:
            with open("../postgres_db/insert_jobs.sql", 'r', encoding='utf-8') as file:
                insert_jobs_sql = file.read()
            with self.conn.cursor() as cur:
                ##基本上jobs內的dict在前面即符合JobModel(可以考慮驗證驗證) 
                for job in jobs:
                    ##其實JobModel應該要跟PG欄位名稱一樣，這裡並沒有做到
                    ##如果欄位衝突的話要怎樣解決，目前是後面直接取代前面    
                    cur.execute(
                    insert_jobs_sql, (
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
                        job['update_date'],  #如果沒有時區資訊會變成系統時區 此處ISO UTC存入
                        job['record_time'],  #如果沒有時區資訊會變成系統時區 此處ISO UTC存入
                        job['source'],  
                        job['keywords'],
                        job['url']  
                    ))
                self.conn.commit()
            print(f'成功將 {len(jobs)} 個職位信息插入到 PostgreSQL 表格中')
        except Exception as e:
          print(f'插入數據庫時出錯: {e}')
          self.conn.rollback()
