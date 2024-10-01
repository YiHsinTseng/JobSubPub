import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
# import time
import pytz
from .base_source import BaseSource
from models.jobs import JobModel

class Source1111(BaseSource):
    def source_url(self, keyword, page):
        base_url = 'https://www.1111.com.tw'
        url = base_url + f'/search/job?ks={keyword}&page={page}'
        return base_url, url

    def parse_source_job(self, base_url, keyword, soup=None, job=None):
        if soup:
            job_list = soup.find_all('div', class_='job-item')##抓錯標籤了
            total_count = int(soup.find('div', class_='left').find("p").find("span").string)
            return {
                "job_list": job_list,
                "total_count": total_count
            }
        elif job:
            # parsing logic specific to 1111
            job_title = job.find('div', class_='title position0').text 
            job_link = base_url + job.find('div', class_='title position0').find("a").get('href')
            company_name = job.find('div', class_='company organ').text.split('|')[0]
            industry = job.find('div', class_='company organ').text.split('|')[1]
            job_desc = job.find('p', class_='introduce').text
            place = job.find('div', class_='other').find("a", attrs={"data-after": True})["data-after"]
            job_salary = job.find('div', class_='other').find("span", attrs={"data-after": True})["data-after"]
            people = job.find('div', class_='people').text[5:].rstrip('人').strip().replace("-", "~")
            taipei_tz = pytz.timezone('Asia/Taipei')
            update = (taipei_tz.localize(datetime.strptime(job.find("div", class_="data").text.strip(), "%Y/%m/%d")).astimezone(pytz.utc)+ timedelta(days=1)).isoformat()##ISO UTC存入但避免存入Date格式又太大誤差故修正

            # Fetch detailed job page
            html_content2 = requests.get(job_link).text
            soup2 = BeautifulSoup(html_content2, 'html.parser')
            
            # Detailed parsing for specific fields 
            job_skill = soup2.find('div', class_='content_items job_skill').find("div", "body_2 description_info")##不小心出錯了
            try:
                job_info = [a.text.strip() for a in job_skill.find("span", class_="job_info_title", text="電腦專長：").find_next_sibling().find_all('a')] 
            except Exception as e:
                job_info = None
            try:
                job_condition = job_skill.find("div", class_="job_info_title", text="附加條件：").find_next_sibling().find("div", class_="ui_items_group").get_text(separator='\n', strip=True)
            except Exception as e:
                job_condition = None
            try:
                job_exp = job_skill.find("span", class_="job_info_title", text="工作經驗：").find_next_sibling().get_text(separator='\n', strip=True)
            except Exception as e:
                job_exp = None
            job_instance = JobModel(
                title=job_title,
                company_name=company_name,
                industry=industry,
                experience=job_exp,
                description=job_desc,
                salary=job_salary,
                applicants=people,
                location=place,
                update_date=update,
                record_time=datetime.now(pytz.utc).isoformat(), ##統一改成ISO8601保留時區資訊
                source="1111",
                keywords=keyword,
                url=job_link,
                requirements=job_info,
                additional_conditions=job_condition
            )
            return job_instance
        else:
            return None
