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
        """用於中斷紀錄(用於從中斷再次啟動)"""
        self.source = source
        self.state_file = f"./data/save_{source.__class__.__name__}.json"
        self.log_file = os.getenv("LOG_FILE", "./data/log.txt")  # 默認值
        self.current_date_string = datetime.now().strftime("%Y%m%d")  # 當前日期字符串 #是否要UTC
        """用於寫入資料庫"""
        self.postgres_handler = PostgresHandler()  # 確保實例化 PostgresHandler
    def search_jobs(self, keyword):
        """每次任務初始化數值"""
        jobs = []
        total_count = 0
        jump = 0
        # skip = []
        # page = 1
        """日誌中斷重啟相關數值"""
        state = load_state(self.state_file, self.current_date_string)
        page = state['page']
        in_page_count = state['in_page_count']
        jobs_count = state['jobs_count']
        """重試機制數值"""
        restart_count=0
        
        start_time = time.time()
        while True:
            try:
                """最早提前停止迴圈控制因素"""
                #手動干預，可前移到迴圈開始
                job_enabled=job_state.is_job_enabled()
                if not job_enabled:  # 每次迴圈都檢查 全局job_enabled
                    print("任務中止") #停止會想馬上開始還是重頭來過
                    break
                #過多錯誤(從錯誤處理catch而來，可前移到迴圈開始)
                if restart_count>=30:
                    print("過度請求導致錯誤")
                    save_state(self.state_file, self.current_date_string,page, total_count, in_page_count, jobs_count+len(jobs),stop_error="True")
                    break #過度錯誤會想馬上人為介入還是重頭來過
                
                """執行任務"""
                """依條件查找向網站請求初步結果"""
                base_url, url = self.source.source_url(keyword, page)##生成查詢連結
                html_content = requests.get(url).text##過度請求失敗
                soup = BeautifulSoup(html_content, 'html.parser')
                """解析並取得查詢結果中的資訊"""
                joblist_dict = self.source.parse_source_job(base_url,keyword,soup=soup)
                job_list = joblist_dict["job_list"]
                total_count = joblist_dict["total_count"]
                """加入提前停止控制因素"""
                #爬蟲超出預期數量(這個就必須在爬蟲階段處理，不能前移)
                ##如果沒有total_count要怎麼推測？
                remaining_count = total_count - jobs_count -len(jobs) - jump
                if remaining_count <= 0:
                    break

                """進入正式解析處理流程"""
                """加入預期解析錯誤處理"""
                #轉由catch再次重置前面的爬蟲步驟
                if not job_list:
                    raise Exception("url錯誤或過度請求")
                
                """解析正常處理流程"""
                restart_count=0
                
                page_jobs = []
                """個別職缺內容處理並寫入資料庫"""
                for job in job_list: ##恢復到上次的地方很麻煩，目前先以頁為主，重複沒關係，本來就應該以頁為單位存，但內存無法記憶
                    try:
                        """
                        由於不同爬蟲的格式可能經過些微變化，因此轉型最好在不同腳本中，這些也可以避免欄位缺失
                        """
                        #資料庫欄位對應格式在內部已經驗證
                        job_instance = self.source.parse_source_job(base_url,keyword, job=job)
                        jobs.append(job_instance.to_dict()) ##全局存
                        page_jobs.append(job_instance.to_dict())## 單頁存
                        #單一職缺寫入成功就加一，失敗就直接跳過不處理
                        in_page_count += 1
                    except Exception as e:
                        print(f'解析職缺資訊失敗: {e}')
                        jump += 1
                        ## skip 此處不會知道具體網址，只會知道是第幾頁的第幾個，錯誤發生在parse中 
                        continue

                ## 單頁存轉存csv append
                #  單頁存轉存PostgreSQL(重新載入還是有可能數量出錯)
                """統一批量寫入解析結果"""
                #page_jobs內的元素需要符合格式(已經在腳本內部經JobModel驗證)
                self.postgres_handler.insert_jobs_into_postgres(page_jobs)
                """以一次批量為單位紀錄日誌"""
                save_state(self.state_file, self.current_date_string, page, total_count, in_page_count, jobs_count+len(jobs),stop_error="False")
                page += 1
            except Exception as e:
                """前面有任何錯誤，就等待再次回到迴圈重試"""
                print(f'請求失敗: {e}')
                restart_count += 1
                
                print("錯誤請求次數:",restart_count)
                if restart_count>=5: #重試次數
                    print("過度請求導致錯誤")
                    time.sleep(120) 
                    continue

                time.sleep(5)
                continue
            
            #正常執行完一次批量紀錄遞迴的參照
            remaining_count = total_count - jobs_count -len(jobs) - jump
            print(f'已獲取職缺數量：{jobs_count+len(jobs)}, 剩餘需要處理的數量：{remaining_count}, 跳過處理數量:{jump}')     
        
        """紀錄最終完成時間以及最終日誌結果"""
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'搜尋耗時: {elapsed_time:.2f} 秒')

        #如果完成或中止的話，就初始化紀錄（目前只要終止就存到log）
        log_state(self.log_file, self.state_file ,self.current_date_string)     
        return total_count, jobs

