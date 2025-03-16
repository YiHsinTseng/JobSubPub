import schedule
import time
from services.scraper import ScraperService
from utils.job_state import scraper_state
from monitor.metrics import JOB_STATUS


def scrape_job(keywords=["Node.js"]):
    job_enabled = scraper_state.is_job_enabled()
    if job_enabled:
        # keywords = ["Node.js"]  # 修改為你需要的關鍵字
        job_service = ScraperService()
        for keyword in keywords:  # 以list輸入關鍵詞
            job_service.fetch_jobs_from_sources(keyword)
    else:
        print("爬蟲任務中止")
        return


def schedule_and_run_jobs():
    scrape_job()
    schedule.every().day.at("01:00").do(scrape_job)
    # schedule.every(2).hours.do(job)


def run_scheduler():
    JOB_STATUS.set(1)
    schedule_and_run_jobs()
    while True:
        schedule.run_pending()
        time.sleep(1)
