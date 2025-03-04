import pandas as pd
from datetime import datetime
from services.jobs import JobService
import os
from utils.source_loader import source_loader

class JobController:
    def __init__(self):
        self.sources = source_loader()  # Dynamically load all sources
        # self.sources= [Source1111()]

    def search_and_save_jobs(self, keyword):
        all_jobs = []
        total_count_all_sources = 0
        
        #TODO - 可以考慮用多執行緒的爬法
        for source in self.sources:
            print(f"正在處理資料來源: {source.__class__.__name__}")
            job_service = JobService(source)  # Create a JobService instance for each source
            total_count, jobs= job_service.search_jobs(keyword)
            
            all_jobs.extend(jobs)
            total_count_all_sources += total_count

        ## csv儲存
        df = pd.DataFrame(all_jobs)
        current_date_time = datetime.now()
        date_string = current_date_time.strftime("%Y%m%d")

        directory = f'data/records'

        if not os.path.exists(directory):
            os.makedirs(directory)

        csv_file_path = f'{directory}/jobs_{date_string}_{keyword}.csv'
        df.to_csv(csv_file_path, header=True, index=False)
        
        return total_count_all_sources, all_jobs

