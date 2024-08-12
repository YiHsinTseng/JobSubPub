from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
# import pandas as pd
import json
# import csv
from .pgUpdateHandler import PostgresHandler

class JobService:
    def __init__(self, source):
        self.source = source
        self.state_file = f"./data/save_{source.__class__.__name__}.json"
        # self.csv_file = "./data/jobs1111_20240807_node.csv"
        self.current_date_string = datetime.now().strftime("%Y%m%d")  # 当前日期字符串
        self.postgres_handler = PostgresHandler()  # 確保實例化 PostgresHandler

    def load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                file_date = state.get('date', None)
                if file_date == self.current_date_string:
                    return state
                else:
                    # 如果日期不匹配，则返回初始状态
                    return {'date': self.current_date_string, 'page': 1, 'in_page_count': 0, 'jobs_count': 0}
        except FileNotFoundError:
            return {'date': self.current_date_string,'page': 1, 'in_page_count': 0,'jobs_count':0}

    def save_state(self, page, total_count, in_page_count, jobs_count):
        state = {'date': self.current_date_string, 'page': page, 'total_count': total_count, 'in_page_count': in_page_count, 'jobs_count': jobs_count}
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    # def save_to_csv(self, jobs, append=False):
    #     mode = 'a' if append else 'w'
    #     header = not append

    #     with open(self.csv_file, mode, newline='', encoding='utf-8') as file:
    #         writer = csv.DictWriter(file, fieldnames=['job_title', 'company', 'location', 'salary', 'description', 'url'])  # Adjust fieldnames as needed
    #         if header:
    #             writer.writeheader()
    #         writer.writerows(jobs)

    def search_jobs(self, keyword):
        jobs = []
        state = self.load_state()
        total_count = 0
        jump = 0
        skip = []
        # page = 1
        page = state['page']
        in_page_count = state['in_page_count']
        jobs_count = state['jobs_count']
        start_time = time.time()

        while True:
            base_url, url = self.source.source_url(keyword, page)
            try:
                html_content = requests.get(url).text
                soup = BeautifulSoup(html_content, 'html.parser')

                joblist_dict = self.source.parse_source_job(base_url,keyword,soup=soup)
                job_list = joblist_dict["job_list"]
                total_count = joblist_dict["total_count"]

                remaining_count = total_count - jobs_count -len(jobs) - jump
                if remaining_count <= 0:
                    break
                
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
                self.save_state(page, total_count, in_page_count, jobs_count+len(jobs))
                page += 1

            except Exception as e:
                print(f'請求失敗: {e}')
                continue

            remaining_count = total_count - jobs_count -len(jobs) - jump
            print(f'已獲取職缺數量：{jobs_count+len(jobs)}, 剩餘需要處理的數量：{remaining_count}, 跳過處理數量:{jump}')     

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'搜尋耗時: {elapsed_time:.2f} 秒')

        return total_count, jobs

