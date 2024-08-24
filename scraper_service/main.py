from controllers.jobs import JobController
import schedule
import time

import threading
from flask import Flask, jsonify

app = Flask(__name__)
# 定义全局变量来控制任务的启停
job_running = True

# def main():
#     keyword = 'node.js'  # 修改為你需要的關鍵字
#     job_controller = JobController()  # 創建 JobController 實例
#     job_controller.search_and_save_jobs(keyword)  # 使用 JobController 進行操作

## db_init 

def job():
    global job_running
    if job_running:
        keyword = 'node.js'  # 修改為你需要的關鍵字
        job_controller = JobController()  # 創建 JobController 實例
        job_controller.search_and_save_jobs(keyword)  # 使用 JobController 進行操作

def main():
    # print("scraper service start")
    schedule.every().day.at("09:00").do(job)  # 每天上午9點執行
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/start_job', methods=['POST'])
def start_job():
    global job_running
    job_running = True
    return jsonify({"status": "Job started"})

@app.route('/stop_job', methods=['POST'])
def stop_job():
    global job_running
    job_running = False
    return jsonify({"status": "Job stopped"})

@app.route('/go_job', methods=['POST'])
def go_job():
    # job()
    threading.Thread(target=job).start()
    ##完成後如何通知
    return jsonify({"status": "Job ongoing"})


if __name__ == "__main__":
    # main()
    # 在一个单独的线程中运行定时任务调度器
    job_thread = threading.Thread(target=main)
    job_thread.start()

     # 啓動Flask應用程序，監聽所有接口(讓docker可以使用)
    app.run(host='0.0.0.0', port=5060)
