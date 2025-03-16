from prometheus_client import start_http_server

from app import create_app

import threading
from tasks.scrape_job_scheduler import run_scheduler


def run_monitor():
    start_http_server(8001)


# 但可以採用工廠模式以及使用配置管理
app = create_app()

if __name__ == "__main__":
    threading.Thread(target=run_monitor, daemon=True).start()
    threading.Thread(target=run_scheduler, daemon=True).start()
    # 只是用於爬蟲指令使用，無併發需求，因此使用自建WSGI
    app.run(
        host="0.0.0.0", port=5060, debug=False
    )  # 讓其他容器也能訪問(打開局域網)，測試模式可能導致非API指令執行兩次
