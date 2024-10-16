import os
import threading
from datetime import datetime
from flask import jsonify
from services.state_manager import log_state
from utils.source_loader import source_loader
from scheduler import job
from monitor.metrics import metrics,JOB_STATUS,REQUEST_COUNT
from job_state import job_state

def init_routes(app):
    @app.route('/metrics')
    def metrics_route():
        return metrics()

    @app.route('/start_job', methods=['POST'])
    def start_job():
        job_state.start_job()
        JOB_STATUS.set(1)  # 設置指標，表示任務已啓動
        return jsonify({"status": "Job started"})

    @app.route('/stop_job', methods=['POST'])
    def stop_job():
        job_state.stop_job()
        JOB_STATUS.set(0)  # 設置指標，表示任務已停止
        return jsonify({"status": "Job stopped"})

    @app.route('/go_job', methods=['POST'])
    def go_job():
        threading.Thread(target=job).start()
        REQUEST_COUNT.inc()  # 每次調用增加請求計數
        return jsonify({"status": "Job ongoing"})

    @app.route('/start_logging', methods=['POST'])
    def start_logging():
        log_file = os.getenv("LOG_FILE", "./data/log.txt")  # 默認值
        current_date_string = datetime.now().strftime("%Y%m%d")

        sources = source_loader() 
        for source in sources:
            state_file = f"./data/save_{source.__class__.__name__}.json"
            log_state(log_file, state_file, current_date_string)
        
        return jsonify({"message": "State Logged."}), 200
