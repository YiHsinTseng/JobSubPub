from repository.job import JobRepository
from .scraper_progress_manager import StateManager
import os
from datetime import datetime

import time

"""Request 錯誤處理層"""
import requests
from utils.request_utils import make_request  # 負責重試

"""處理職缺爬蟲任務邏輯，通常可以被Scrapy替代?"""
from bs4 import BeautifulSoup

from utils.job_state import scraper_state


class JobService:
    def __init__(self, source, keyword):
        self.source = source
        self.source_name = source.__class__.__name__
        self.keyword = keyword
        self.job_repository = JobRepository()
        """紀錄爬蟲狀態"""
        self.scraper_progress_manager = StateManager(
            f"./data/save_{source.__class__.__name__}_{keyword}.json"  # 單腳本紀錄
        )  # 思考keyword是不是要這樣耦合
        self.log_file = os.getenv("LOG_FILE", "./data/log.txt")  # 多腳本共同紀錄
        self.current_date_string = datetime.now().strftime(
            "%Y%m%d"
        )  # 當前日期字符串 #是否要UTC

    def search_jobs(self, keyword):  # 思考keyword是不是要這樣耦合
        total_parsed_jobs = []

        skipped_jobs = 0
        """狀態管理層"""
        # 過去狀態(用於轉換成未來儲存，作為不可變數不再賦值)
        prev_state = self.scraper_progress_manager.load(
            self.current_date_string
        )  # 開算前取
        # 當前狀態(用於未來儲存)
        current_state = {  # 開算後存
            "date": self.current_date_string,
            "total_count": prev_state.get("total_count", 0),
            "daily_inserted_count": prev_state.get("daily_inserted_count", 0),
            "last_page": (
                prev_state.get("last_page", None)
            ),  # 爬蟲後才會知道，先給個預設值
            "page": prev_state.get("page", 0) + 1,  # 當前假定一定有爬完(正在爬)
            "last_inserted_count": 0,
            "page_failed": False,
        }

        start_time = time.time()
        page_fail_count = 0
        """Job LIST 錯誤處理層(全局重試迴圈)"""
        while True:
            try:
                job_enabled = scraper_state.is_job_enabled()
                if not job_enabled:
                    print(f"[ {self.source_name} - {keyword} ] 任務因為管理員手動停止")
                    break

                url = self.source.make_query_url(keyword, current_state["page"])
                # print(
                #     f"[ {self.source_name} - {keyword} ] 當前爬取頁數：",
                #     current_state["page"],
                # )
                response = make_request(url)
                response.raise_for_status()

                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                joblist_dict = self.source.parse_job_list_page(keyword, soup)
                current_state["total_count"] = joblist_dict["total_count"]
                job_list = joblist_dict["job_list"]

                remaining = (
                    current_state["total_count"]
                    - prev_state["daily_inserted_count"]
                    - current_state["last_inserted_count"]
                    - skipped_jobs
                )

                current_state["last_page"] = joblist_dict.get("last_page", None)

                if current_state["last_page"] is None:
                    if (
                        remaining <= 0
                        or current_state["total_count"]
                        < current_state["last_inserted_count"]
                    ):
                        current_state["page"] = current_state["page"] - 1
                        print("已達成爬取目標或超出預期數量，結束爬取")
                        break
                else:
                    if current_state["page"] > current_state["last_page"]:
                        print("已達成爬取目標或超出預期數量，結束爬取")
                        current_state["page"] = current_state["page"] - 1
                        break

                if not job_list:
                    raise ValueError("無法取得職缺列表，可能為網址錯誤或過度請求")

                total_parsed_jobs, skipped_jobs = self._process_job_entries(
                    job_list, keyword, skipped_jobs
                )

                if total_parsed_jobs:
                    self.job_repository.insert_jobs_into_postgres(total_parsed_jobs)
                    current_state["last_inserted_count"] += len(total_parsed_jobs)

                current_state["daily_inserted_count"] = (
                    prev_state["daily_inserted_count"]
                    + current_state["last_inserted_count"]
                )

                self.scraper_progress_manager.save(current_state)
                page_fail_count = 0

            except Exception as e:
                page_fail_count += 1
                current_state["page_failed"] = True
                # 不同爬蟲等待策略
                print(
                    f"[ {self.source_name} - {keyword} ] job_list [第 {current_state['page']} 頁] 錯誤次數 {page_fail_count} 次: {e}"
                )
                if page_fail_count in [0, 2]:
                    print(f"暫停一段時間以防止被封鎖 (錯誤 {page_fail_count} 次)")
                    time.sleep(30)

                if page_fail_count >= 2:
                    print("多次失敗，中止爬取，需人工檢查")
                    current_state["page"] = current_state["page"] - 1
                    self.scraper_progress_manager.save(current_state)
                    break
                time.sleep(5)

            remaining = (
                current_state["total_count"]
                - prev_state["daily_inserted_count"]
                - current_state["last_inserted_count"]
                - skipped_jobs
            )

            # 紀錄當前迴圈爬取進度
            print(
                f"[ {self.source_name} - {keyword} ] 頁數進度: {current_state['page']} / {current_state['last_page']}，累計職缺數: {current_state['daily_inserted_count']} / {current_state['total_count']}，跳過數: {skipped_jobs}，剩餘數量: {remaining}"
            )
            # 沒有錯誤才會移到下一頁
            if current_state["page_failed"] == False:
                current_state["page"] += 1

        elapsed_time = time.time() - start_time
        print(f"[ {self.source_name} - {keyword} ] 任務耗時: {elapsed_time:.2f} 秒")

        self.scraper_progress_manager.log(self.log_file)
        return current_state["total_count"], total_parsed_jobs

    def _process_job_entries(self, job_list, keyword, skipped_jobs):
        """Job ITEM 錯誤處理層"""
        # 明確爬蟲解析錯誤處理方式，目前沒有跳過機制，但保留變數
        parsed_page_jobs = []
        for idx, job in enumerate(job_list):
            try:
                job_object = self.source.parse_job_detail(keyword, job)
                job_dict = job_object.to_dict()
                parsed_page_jobs.append(job_dict)  # 曾經爬過還是會存
            except requests.exceptions.HTTPError as e:
                print(
                    f"[ {self.source_name} - {keyword} ] job_entry [HTTP 錯誤] 第 {idx + 1} 筆職缺解析失敗: {e}"
                )
                # skipped_jobs.append(job)  # 記錄錯誤職缺並跳過
                raise
            except requests.exceptions.ConnectionError as e:
                print(
                    f"[ {self.source_name} - {keyword} ] job_entry [Connection 錯誤] 第 {idx + 1} 筆職缺解析失敗: {e}"
                )
                # skipped_jobs.append(job)  # 記錄錯誤職缺並跳過
                raise
            except Exception as e:
                print(
                    f"[ {self.source_name} - {keyword} ] job_entry [解析錯誤] 第 {idx + 1} 筆職缺解析失敗: {e}"
                )
                # skipped_jobs.append(job)  # 記錄錯誤職缺並跳過
                raise
        return parsed_page_jobs, skipped_jobs
