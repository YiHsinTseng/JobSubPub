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
  
  ## 現在是以頁為單位插入PG，沒有用job_link作為PK以職缺為單位更新
  def insert_jobs_into_postgres(self, jobs):
      try:
          with self.conn.cursor() as cur:
              for job in jobs:
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