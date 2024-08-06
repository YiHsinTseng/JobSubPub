from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from models.jobs import JobModel

class JobService:
    def __init__(self, source):
        self.source = source

    def search_jobs(self, keyword):
        jobs = []
        total_count = 0
        jump = 0
        skip = []
        page = 1
        start_time = time.time()

        while True:
            base_url, url = self.source.soruce_url(keyword, page)
            try:
                html_content = requests.get(url).text
                soup = BeautifulSoup(html_content, 'html.parser')

                joblist_dict = self.source.parse_source_job(base_url, soup=soup)
                job_list = joblist_dict["job_list"]

                ##分析爬蟲時間
                total_count = joblist_dict["total_count"]
                remaining_count = total_count - len(jobs) - jump
                print (f'total_count: {total_count}, len(jobs): {len(jobs)}, remaining_count: {remaining_count}')

                if remaining_count <= 0:
                    break

                for job in job_list:
                    try:
                        # job_dict = self.source.parse_source_job(base_url, job=job)
                        # jobs.append({
                        #     '職缺名稱': job_dict['職缺名稱'],
                        #     '公司名稱': job_dict['公司名稱'],
                        #     "產業": job_dict["產業"],
                        #     "年資": job_dict["年資"],
                        #     '職缺描述': job_dict["職缺描述"],
                        #     "工作要求": job_dict["工作要求"],
                        #     "附加條件": job_dict["附加條件"],
                        #     '薪資': job_dict["薪資"],
                        #     "應徵人數": job_dict["應徵人數"],
                        #     "地區": job_dict["地區"],
                        #     "更新日期": job_dict["更新日期"],
                        #     "紀錄時間": job_dict["紀錄時間"],
                        #     "來源": job_dict["來源"],
                        #     "職缺網址": job_dict["職缺網址"]
                        # })
                        job_instance = self.source.parse_source_job(base_url, job=job)
                        jobs.append(job_instance.to_dict())
                    except Exception as e:##有錯就會直接跳過
                        print(f'解析職缺資訊失敗: {e}')
                        jump += 1
                        # skip.append(job_dict["職缺網址"])
                        continue

                page += 1

            except Exception as e:
                print(f'請求失敗: {e}')
                total_count = 0
                continue

        ##分析爬蟲時間
        remaining_count = total_count - len(jobs) - jump
        print(f'已獲取職缺數量：{len(jobs)}, 剩餘需要處理的數量：{remaining_count},跳過處理數量:{jump}')     
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'搜尋耗時: {elapsed_time:.2f} 秒')

        # df = pd.DataFrame(jobs)
        # current_date_time = datetime.now()
        # date_string = current_date_time.strftime("%Y%m%d")
        # df.to_csv(f'data/jobs_{date_string}.csv', header=True, index=False)
        return total_count, jobs, skip
