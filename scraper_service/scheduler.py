import schedule
import time
import threading
from monitor.metrics import JOB_STATUS
from controllers.jobs import JobController
from job_state import job_state

def job():
    job_enabled=job_state.is_job_enabled()
    if job_enabled:
        keyword = 'Node.js'  # 修改為你需要的關鍵字
        job_controller = JobController() 
        job_controller.search_and_save_jobs(keyword)

def schedule_jobs():
    job()
    schedule.every().day.at("01:00").do(job)
    # schedule.every(2).hours.do(job)

def run_scheduler():
    JOB_STATUS.set(1)
    schedule_jobs()
    while True:
        schedule.run_pending()
        time.sleep(1)