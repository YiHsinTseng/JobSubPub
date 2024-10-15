from controllers.jobs import JobController
import schedule
import time
from datetime import datetime


from prometheus_client import start_http_server, Summary, Counter, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from flask import Response

import threading
from flask import Flask, jsonify

import os
from dotenv import load_dotenv
load_dotenv()

from config import config

from services.state_manager import log_state,load_state

REQUEST_COUNT = Counter('flask_app_requests_total', 'Total number of requests')
JOB_STATUS = Gauge('job_status', 'Whether the job is running (1) or stopped (0)')
JOB_DURATION = Summary('job_duration_seconds', 'Time spent processing job')

app = Flask(__name__)

def job():
    if config.job_running:
        keyword = 'Node.js'  # 修改為你需要的關鍵字
        job_controller = JobController() 
        job_controller.search_and_save_jobs(keyword)

def main():
    job()
    schedule.every().day.at("01:00").do(job)
    #schedule.every(2).hours.do(job)
    JOB_STATUS.set(1)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/start_job', methods=['POST'])
def start_job():
    config.job_running = True
    JOB_STATUS.set(1)  # 設置指標，表示任務已啓動
    return jsonify({"status": "Job started"})

@app.route('/stop_job', methods=['POST'])
def stop_job():
    config.job_running = False
    JOB_STATUS.set(0)  # 設置指標，表示任務已停止
    return jsonify({"status": "Job stopped"})

@app.route('/go_job', methods=['POST'])
def go_job():
    # job()
    threading.Thread(target=job).start()
    REQUEST_COUNT.inc()  # 每次調用增加請求計數
    ##完成後如何通知
    return jsonify({"status": "Job ongoing"})

from utils.source_loader import source_loader

@app.route('/start_logging', methods=['POST'])
def start_logging():
    log_file = os.getenv("LOG_FILE", "./data/log.txt")  # 默認值
    current_date_string = datetime.now().strftime("%Y%m%d")

    sources = source_loader() 
    for source in sources:
        state_file = f"./data/save_{source.__class__.__name__}.json"
        state = load_state(state_file, current_date_string)
        log_state(log_file, state_file, current_date_string)
    
    return jsonify({"message": "State Logged."}), 200

def run_app():
    app.run(port=5000)  # 可以根据需要更改端口


if __name__ == "__main__":
    # main()
    start_http_server(8001)
    # 在一個單獨的線程中運行定時任務調度器
    job_thread = threading.Thread(target=main)
    job_thread.start()

     # 啓動Flask應用程序，監聽所有接口(讓docker可以使用)
    app.run(host='0.0.0.0', port=5060)
