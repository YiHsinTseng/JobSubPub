"""處理通用爬蟲任務邏輯"""

from services.job_scraper import JobService
from utils.source_loader import source_loader


class ScraperService:
    def __init__(self):
        self.sources = source_loader()

    def fetch_jobs_from_sources(self, keyword):
        # 以list接收關鍵詞
        all_jobs = []
        total_count_all_sources = 0

        for source in self.sources:
            print(f"正在處理資料來源: {source.__class__.__name__}")
            job_service = JobService(source, keyword)
            total_count, jobs = job_service.search_jobs(keyword)

            all_jobs.extend(jobs)
            total_count_all_sources += total_count

        # return total_count_all_sources, all_jobs
