from datetime import datetime
import pytz
from .base_source import BaseSource
from utils.request_utils import make_job_request
from models.jobs import JobModel


class Source104(BaseSource):
    """來源網站查詢url的形式"""

    BASE_URL = f"https://www.104.com.tw"
    # 暫時這樣改
    global_page = 1

    def make_query_url(self, keyword, page):
        """但實際根據api取得資料"""
        url = (
            self.BASE_URL
            + f"/jobs/search/?ro=1&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}"
        )
        # 暫時這樣改
        global global_page
        global_page = page

        # api_url = (
        #     self.BASE_URL
        #     + f"https://www.104.com.tw/jobs/search/api/jobs?filterLabels=c%402025career&jobsource=2018indexpoc&keyword={keyword}&kwop=7&mode=s&orLabel=c%402025career%5E5&order=15&page={page}&pagesize=20&ro=1"
        # )

        # url = BASE_URL+f'/jobs/search/?ro=1&isnew=0&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
        #   https://www.104.com.tw/jobs/search/?ro=1&kwop=7&keyword=node.js&mode=s&jobsource=2018indexpoc&page=1
        # print(url)
        return url

    """解析soup的規則"""

    def parse_job_list_page(self, keyword, soup):
        """
        解析職缺列表頁面，也包含API額外取得總數、頁數資訊
        """

        ## 問題在於使用html joblist來取值
        ## 首頁html要能work才能執行，現在需要改成api取值了
        ##job_list = soup.find_all("div", class_="job-list-container")

        # 暫時這樣改
        global global_page
        page = global_page

        api_url = (
            self.BASE_URL
            + f"/jobs/search/api/jobs?jobsource=2018indexpoc&keyword={keyword}&kwop=7&mode=s&order=15&page={page}&pagesize=20&ro=1"
        )
        print(page)

        data = make_job_request(api_url).json()

        total_count = data.get("metadata", {}).get("pagination", {}).get("total", 0)
        last_page = data.get("metadata", {}).get("pagination", {}).get("lastPage", 1)
        job_list = data.get("data", {})  # 暫時方案，至少數量正確

        return {
            "job_list": job_list,
            "total_count": total_count,
            "last_page": last_page,
        }

    def parse_job_detail(self, keyword, job):
        """
        解析單一職缺詳情，也包含主頁爬取資料與API補充資料
        """
        try:
            # job_title = job.find("a", class_="info-job__text").text.strip()
            # job_link = job.find("a", class_="info-job__text")["href"]
            # company_name = job.find("a", class_="info-company__text").text.strip()
            # industry = job.find("span", class_="info-company-addon-type").text.strip()
            # job_desc_preview = job.find("div", class_="info-description").text.strip()
            # job_exp = job.find("a", href=lambda x: x and "jobexp" in x).text.strip()

            # # 薪資
            # job_salary_element = job.find(
            #     "a",
            #     attrs={"data-gtm-joblist": lambda x: x and x.startswith("職缺-薪資")},
            # )
            # job_salary = job_salary_element.text.strip() if job_salary_element else None

            # # 申請人數
            # people = job.find("a", class_="action-apply__range")
            # applicants = (
            #     people.text.strip()[:-2].rstrip("人").strip() if people else None
            # )

            # # 工作地點
            # place = job.find("span", class_="info-tags__text").text.strip()

            # 但是這連結沒有跟著page
            job_link = job["link"]["job"]  # 暫時方案，雖然這樣會多發一次API
            # print(job_link)
            # API 補充詳細資料
            api_data = make_job_request(job_link).json().get("data", {})
            job_title = api_data["header"]["jobName"]
            company_name = api_data["header"]["custName"]
            industry = job.get("coIndustryDesc", "")
            job_desc_preview = api_data["jobDetail"]["jobDescription"]
            job_exp = api_data["condition"].get("workExp", "")

            # 薪資
            job_salary = api_data["jobDetail"]["salary"]

            # 申請人數（假設沒有提供直接欄位，可以先設 None 或 0）

            ranges = [
                (0, 5, "0~5"),
                (6, 10, "6~10"),
                (11, 30, "11~30"),
                (31, 50, "31~50"),
            ]
            people = api_data["header"].get("userApplyCount", 0)
            applicants = next(
                (label for start, end, label in ranges if start <= people <= end), "50+"
            )

            # 工作地點
            place = api_data["jobDetail"]["addressRegion"]

            job_info = [
                item.get("description")
                for item in api_data.get("condition", {}).get("specialty", [])
            ]
            job_condition = api_data.get("condition", {}).get("other")
            update = api_data.get("header", {}).get("appearDate")
            job_desc = api_data.get("jobDetail", {}).get(
                "jobDescription", job_desc_preview
            )

            # 經歷年數對應表
            job_exp_mapping = {
                "不拘": 0,
                "經歷不拘": 0,
                **{f"{i}年以上": i for i in range(1, 11)},
            }

            if not update:
                print(f"[警告] 無法取得更新日期，可能職缺已關閉: {job_link}")

            # 組成 JobModel 格式
            job_data = {
                "title": job_title,
                "company_name": company_name,
                "industry": industry,
                "experience": job_exp,
                "experience_year": job_exp_mapping.get(job_exp, None),
                "description": job_desc,
                "requirements": job_info,
                "additional_conditions": job_condition,
                "salary": job_salary,
                "applicants": applicants,
                "location": place,
                "update_date": update,
                "record_time": datetime.now(pytz.utc).isoformat(),  # ISO 格式
                "source": "104",
                "keywords": keyword,
                "url": job_link,
            }

            # 回傳 Pydantic 模型，利於驗證
            return JobModel(**job_data)

        except Exception as e:
            print(f"[錯誤] 解析職缺失敗: {e} | 職缺連結: {job_link}")
            return None
