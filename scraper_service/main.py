from controllers.jobs import JobController
import schedule
import time

from prometheus_client import start_http_server, Summary, Counter, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from flask import Response

import threading
from flask import Flask, jsonify

REQUEST_COUNT = Counter('flask_app_requests_total', 'Total number of requests')
JOB_STATUS = Gauge('job_status', 'Whether the job is running (1) or stopped (0)')
JOB_DURATION = Summary('job_duration_seconds', 'Time spent processing job')

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
    job()
    schedule.every().day.at("09:00").do(job)  # 每天上午9點執行
    JOB_STATUS.set(1)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/start_job', methods=['POST'])
def start_job():
    global job_running
    job_running = True
    JOB_STATUS.set(1)  # 設置指標，表示任務已啓動
    return jsonify({"status": "Job started"})

@app.route('/stop_job', methods=['POST'])
def stop_job():
    global job_running
    job_running = False
    JOB_STATUS.set(0)  # 設置指標，表示任務已停止
    return jsonify({"status": "Job stopped"})

@app.route('/go_job', methods=['POST'])
def go_job():
    # job()
    threading.Thread(target=job).start()
    REQUEST_COUNT.inc()  # 每次調用增加請求計數
    ##完成後如何通知
    return jsonify({"status": "Job ongoing"})


if __name__ == "__main__":
    # main()
    start_http_server(8001)
    # 在一個單獨的線程中運行定時任務調度器
    job_thread = threading.Thread(target=main)
    job_thread.start()

     # 啓動Flask應用程序，監聽所有接口(讓docker可以使用)
    app.run(host='0.0.0.0', port=5060)
