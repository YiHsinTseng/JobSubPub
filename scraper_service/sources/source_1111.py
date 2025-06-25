from datetime import datetime
import pytz
from .base_source import BaseSource
from utils.request_utils import make_job_request
from models.jobs import JobModel

from bs4 import BeautifulSoup
import re


class Source1111(BaseSource):
    """來源網站查詢url的形式"""

    BASE_URL = "https://www.1111.com.tw"

    def make_query_url(self, keyword, page):

        url = self.BASE_URL + f"/search/job?ks={keyword}&page={page}"
        # print(url)
        return url

    """解析soup的規則"""

    def parse_job_list_page(self, keyword, soup):
        """
        解析職缺列表頁面，也包含API額外取得總數、頁數資訊
        """

        job_list = soup.find_all("div", class_="job-card")

        meta_description = soup.find("meta", attrs={"name": "description"})
        total_count_match = (
            re.search(r"\((\d+)\)\s*個工作職缺機會", meta_description["content"])
            if meta_description
            else None
        )
        total_count = int(total_count_match.group(1)) if total_count_match else 0

        return {"job_list": job_list, "total_count": total_count}

    def parse_job_detail(self, keyword, job):
        """
        解析單一職缺詳情，也包含主頁爬取資料與API補充資料
        """
        # parsing logic specific to 1111
        job_title = job.find("h2").get_text(strip=True)
        job_link = self.BASE_URL + job.find("a")["href"]

        company_text = (
            job.find("div", class_="line-clamp-1").get_text(strip=True).split("｜")
        )
        company_name = company_text[0].strip()
        industry = company_text[1].strip() if len(company_text) > 1 else None
        # place_elements = job.select("a.hover\:underline")
        # place = (
        #     place_elements[2].get_text(strip=True) if len(place_elements) > 2 else None
        # )
        place = job.find("h4", class_="job-card-condition__text").get_text(strip=True)

        people_text = (
            job.find("div", class_="job-summary").get_text(strip=True).split("｜")
        )
        people = (
            people_text[1]
            .replace("人應徵", "")
            .replace("-", "~")
            .replace(" ", "")
            .strip()
            if len(people_text) > 1
            else None
        )

        update_date_str = people_text[0].replace(" / ", "/").strip()

        try:
            taipei_tz = pytz.timezone("Asia/Taipei")
            update = datetime.strptime(update_date_str, "%m/%d")
            current_year = datetime.now().year
            update = update.replace(year=current_year)
            update = taipei_tz.localize(update).date().isoformat()
        except ValueError:
            print("無效日期格式")
            update = None

        # Detailed parsing for specific fields
        html_content2 = make_job_request(job_link).text
        soup2 = BeautifulSoup(html_content2, "html.parser")
        job_desc = soup2.select_one("div.content div.whitespace-pre-line").get_text(
            strip=True
        )

        job_salary = soup2.select_one("div.text-main").contents[0].strip()

        job_skill = soup2.find("section", {"id": "REQUIREMENTS"})

        """鏈式取值除錯"""
        try:
            job_info = [
                li.get_text(strip=True).strip("、")
                for li in job_skill.find("p", string="電腦專長")
                .find_next("ul")
                .find_all("li")
            ]
        except Exception as e:
            job_info = []

        try:
            job_condition = (
                job_skill.find("p", string="工作技能")
                .find_next("p")
                .get_text(strip=True)
            )
        except Exception as e:
            job_condition = None

        try:
            job_exp = (
                job_skill.find("h3", string="工作經驗")
                .find_next("p")
                .get_text(strip=True)
                .replace(" ", "")
            )
        except Exception as e:
            job_exp = None

        # print(job_exp)

        # 映射工作經驗的年數
        job_exp_mapping = {
            "經歷不拘": 0,
            "不拘": 0,
            "半年經驗": 1,
            **{f"{i}年以上": i for i in range(1, 11)},  # 自動生成 1~10 年
            **{f"{i}年以上經驗": i for i in range(1, 11)},  # 自動生成 1~10 年
        }

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
            "applicants": people,
            "location": place,
            "update_date": update,
            "record_time": datetime.now(
                pytz.utc
            ).isoformat(),  # 使用 ISO8601 格式保留時區資訊
            "source": "1111",
            "keywords": keyword,
            "url": job_link,
        }

        # 利於資料庫寫入時的資料驗證，要為了確保不同腳本沒有遺漏欄位，並且格式要正確。
        job_instance = JobModel(**job_data)
        return job_instance
