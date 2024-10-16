from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
from .pgUpdateHandler import PostgresHandler
from .state_manager import log_state ,load_state,save_state
from job_state import job_state

import os
from dotenv import load_dotenv

# 加載 .env 文件中的環境變量
load_dotenv()

class JobService:
    def __init__(self, source):
        self.source = source
        self.state_file = f"./data/save_{source.__class__.__name__}.json"
        self.log_file = os.getenv("LOG_FILE", "./data/log.txt")  # 默認值
        self.current_date_string = datetime.now().strftime("%Y%m%d")  # 當前日期字符串 #是否要UTC
        self.postgres_handler = PostgresHandler()  # 確保實例化 PostgresHandler

    def search_jobs(self, keyword):
        jobs = []
        state = load_state(self.state_file, self.current_date_string)
        total_count = 0
        jump = 0
        skip = []
        # page = 1
        page = state['page']
        in_page_count = state['in_page_count']
        jobs_count = state['jobs_count']
        start_time = time.time()
        restart_count=0

        while True:
            base_url, url = self.source.source_url(keyword, page)##生成查詢連結
            try:
                html_content = requests.get(url).text##過度請求失敗
                soup = BeautifulSoup(html_content, 'html.parser')

                joblist_dict = self.source.parse_source_job(base_url,keyword,soup=soup)
                job_list = joblist_dict["job_list"]
                total_count = joblist_dict["total_count"]
                job_enabled=job_state.is_job_enabled()
                if not job_enabled:  # 每次迴圈都檢查 全局job_enabled
                    print("任務中止") #停止會想馬上開始還是重頭來過
                    break
                if restart_count>=30:
                    print("過度請求導致錯誤")
                    save_state(self.state_file, self.current_date_string,page, total_count, in_page_count, jobs_count+len(jobs),stop_error="True")
                    break #過度錯誤會想馬上人為介入還是重頭來過
                #如果沒有total_count要怎麼推測？
                remaining_count = total_count - jobs_count -len(jobs) - jump
                if remaining_count <= 0:
                    break

                if not job_list:
                    raise Exception("url錯誤或過度請求")
                restart_count=0
                
                page_jobs = []
                for job in job_list: ##恢復到上次的地方很麻煩，目前先以頁為主，重複沒關係，本來就應該以頁為單位存，但內存無法記憶
                    try:
                        job_instance = self.source.parse_source_job(base_url,keyword, job=job)
                        jobs.append(job_instance.to_dict()) ##全局存
                        page_jobs.append(job_instance.to_dict())## 單頁存
                        in_page_count += 1
                    except Exception as e:
                        print(f'解析職缺資訊失敗: {e}')
                        jump += 1
                        ## skip 此處不會知道具體網址，只會知道是第幾頁的第幾個，錯誤發生在parse中 
                        
                        continue

                ## 單頁存轉存csv append
                #  單頁存轉存PostgreSQL(重新載入還是有可能數量出錯)
                self.postgres_handler.insert_jobs_into_postgres(page_jobs)
                save_state(self.state_file, self.current_date_string, page, total_count, in_page_count, jobs_count+len(jobs),stop_error="False")
                page += 1
            except Exception as e:
                print(f'請求失敗: {e}')
                restart_count += 1
                
                print("錯誤請求次數:",restart_count)
                if restart_count>=5: #重試次數
                    print("過度請求導致錯誤")
                    time.sleep(120) 
                    continue

                time.sleep(5)
                continue

            remaining_count = total_count - jobs_count -len(jobs) - jump
            print(f'已獲取職缺數量：{jobs_count+len(jobs)}, 剩餘需要處理的數量：{remaining_count}, 跳過處理數量:{jump}')     

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'搜尋耗時: {elapsed_time:.2f} 秒')

        #如果完成或中止的話，就初始化紀錄（目前只要終止就存到log）
        log_state(self.log_file, self.state_file ,self.current_date_string)     
        return total_count, jobs

