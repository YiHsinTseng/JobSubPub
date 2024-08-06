import pandas as pd
from datetime import datetime
from services.jobs import JobService
from sources.source_1111 import Source1111
from sources.source_104 import Source104

class JobController:
    def __init__(self):
        self.source = Source1111()  # 創建 Source1111 實例
        # self.source = Source104()  # 創建 Source104 實例
        self.job_service = JobService(self.source)  # 創建 JobService 實例並傳遞 Source1111 實例

    def search_and_save_jobs(self, keyword):
        total_count, jobs, skip = self.job_service.search_jobs(keyword)
        print(f"Total Count: {total_count}")

        ## csv儲存
        df = pd.DataFrame(jobs)
        current_date_time = datetime.now()
        date_string = current_date_time.strftime("%Y%m%d")
        df.to_csv(f'data/jobs1111_{date_string}_{keyword}.csv', header=True, index=False)
        
        # print(f"Skipped URLs: {skip}")
        # return total_count, jobs, skip  # 如果需要返回這些信息

