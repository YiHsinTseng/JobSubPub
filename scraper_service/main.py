from controllers.jobs import JobController
import schedule
import time

# def main():
#     keyword = 'node.js'  # 修改為你需要的關鍵字
#     job_controller = JobController()  # 創建 JobController 實例
#     job_controller.search_and_save_jobs(keyword)  # 使用 JobController 進行操作

def job():
    keyword = 'node.js'  # 修改為你需要的關鍵字
    job_controller = JobController()  # 創建 JobController 實例
    job_controller.search_and_save_jobs(keyword)  # 使用 JobController 進行操作

def main():
    schedule.every().day.at("09:00").do(job)  # 每天上午9點執行

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
