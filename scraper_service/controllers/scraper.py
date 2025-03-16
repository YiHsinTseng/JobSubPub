from flask import jsonify
from tasks.scrape_job_scheduler import scrape_job
from utils.job_state import scraper_state
from monitor.metrics import metrics, JOB_STATUS, REQUEST_COUNT
import threading

# 如果沒有使用blueprint，就不好有前綴

is_scraping = False
scraping_lock = threading.Lock()


def scraper_routes(app):
    @app.route("/scrape", methods=["GET"])
    @app.route("/scrape/<keywords>", methods=["GET"])
    def start_scrape(keywords=None):
        global is_scraping
        MAX_KEYWORD = 2
        # 批量兩種不同關鍵字
        # 通常空格代表OR
        if keywords is None:
            keywords_list = ["Node.js"]
        else:
            keywords_list = keywords.split(",")
            if len(keywords_list) > MAX_KEYWORD:
                return (
                    f"關鍵字數量超過最大限制！最多只能輸入 {MAX_KEYWORD} 個關鍵字。",
                    400,
                )
        # 避免並行爬蟲問題
        print("全局鎖狀態:", is_scraping)
        with scraping_lock:
            if is_scraping:
                return "爬蟲任務正在運行中，請稍後再試。", 400
            is_scraping = True

        # 啟動新的爬蟲任務(類似callback寫法)
        def wrapper():
            try:
                scrape_job(keywords_list)
            finally:
                with scraping_lock:
                    global is_scraping  # 記得全局變數概念
                    is_scraping = False  # 任務完成後重置爬蟲狀態
                    print("全局鎖狀態:", is_scraping)

        threading.Thread(target=wrapper).start()
        # threading.Thread(target=scrape_job, args=(keywords_list,)).start()

        # scraper_service = ScraperService()
        # scraper_service.fetch_jobs_from_sources("Nodejs")
        return jsonify({"status": "Scraping started"})

    @app.route("/status/enable", methods=["GET"])
    def enable_scrape_status():
        scraper_state.start_job()
        JOB_STATUS.set(1)  # 設置指標，表示任務已啓動
        return jsonify({"status": "Scraping enabled"})

    @app.route("/status/disable", methods=["GET"])
    def disable_scrape_status():
        scraper_state.stop_job()
        JOB_STATUS.set(0)  # 設置指標，表示任務已停止
        return jsonify({"status": "Scraping disabled"})
