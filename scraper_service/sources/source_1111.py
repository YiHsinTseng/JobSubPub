import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
# import time
import pytz
from .base_source import BaseSource
from models.jobs import JobModel
import re

class Source1111(BaseSource):
    """客製化個別網站參數url"""
    def source_url(self, keyword, page):
        base_url = 'https://www.1111.com.tw'
        url = base_url + f'/search/job?ks={keyword}&page={page}'
        return base_url, url
    """解析soup的規則""" 
    def parse_source_job(self, base_url, keyword, soup=None, job=None):
        #解析單頁條件查詢結果
        if soup:
            job_list = soup.find_all('div', class_='job-card')

            # 修正 total_count 的抓取方式
            meta_description = soup.find('meta', attrs={'name': 'description'})
            total_count_match = re.search(r'約(\d+)筆', meta_description['content']) if meta_description else None
            total_count = int(total_count_match.group(1)) if total_count_match else 0
            return {
                "job_list": job_list,
                "total_count": total_count
            }
        #解析個別工作資訊框以及其個別頁面結果
        elif job:
            # parsing logic specific to 1111
            job_title = job.find('h2').get_text(strip=True)
            job_link = base_url + job.find('a')['href']
            
            company_text = job.find('div', class_='line-clamp-1').get_text(strip=True).split('|')
            company_name = company_text[0].strip()
            industry = company_text[1].strip() if len(company_text) > 1 else None
        
            place_elements = job.select('a.hover\:underline')
            place = place_elements[2].get_text(strip=True) if len(place_elements) > 2 else None

            people_text = job.find('div', class_='leading-[24px]').get_text(strip=True).split('|')
            people = (people_text[1][5:].replace('人', '').replace('-', '~').strip()
                    if len(people_text) > 1 else None)
            
            update_date_str = job.find('div', class_='text-gray-600').get_text(strip=True).replace(" / ", "/")

            try:
                taipei_tz = pytz.timezone('Asia/Taipei')
                update = datetime.strptime(update_date_str, "%Y/%m/%d")
                current_year = datetime.now().year
        
                update = update.replace(year=current_year)
                print(update)
                update = taipei_tz.localize(update).date().isoformat()
            except ValueError:
                print("無效日期格式")
                update = None
            # Fetch detailed job page
            #分析個別工作頁面結果(更詳細結果)：透過解析HTML
            html_content2 = requests.get(job_link).text
            soup2 = BeautifulSoup(html_content2, 'html.parser')
            
            # Detailed parsing for specific fields 
            job_desc = soup2.select_one('div.content div.whitespace-pre-line').get_text(strip=True)

            job_salary = soup2.select_one('div.text-main').contents[0].strip()

            job_skill = soup2.find('section', {'id': 'REQUIREMENTS'})#.find("div", class_="body_2 description_info")

            try:
                job_info = [li.get_text(strip=True).strip('、') for li in job_skill.find('p', string='電腦專長').find_next('ul').find_all('li')]     
            except Exception as e:
                job_info = []
            try:
                job_condition = job_skill.find('p', string='工作技能').find_next('p').get_text(strip=True)
            except Exception as e:
                job_condition = None
            try:
                job_exp = job_skill.find('p', string='工作經驗').find_next('p').get_text(strip=True)
            except Exception as e:
                job_exp = None
            
            # 映射工作經驗的年數
            job_exp_mapping = {
                "經歷不拘": 0,
                "不拘": 0,
                **{f"{i}年以上": i for i in range(1, 11)},  # 自動生成 1~10 年
                **{f"{i}年以上工作經驗": i for i in range(1, 11)}  # 自動生成 1~10 年
            }

            job_data = {
                "title": job_title,
                "company_name": company_name,
                "industry": industry,
                "experience": job_exp,
                "experience_year":job_exp_mapping.get(job_exp, None),
                "description": job_desc,
                "requirements": job_info,
                "additional_conditions": job_condition,
                "salary": job_salary,
                "applicants": people,
                "location": place,
                "update_date": update,
                "record_time": datetime.now(pytz.utc).isoformat(),  # 使用 ISO8601 格式保留時區資訊
                "source": "1111",
                "keywords": keyword,
                "url": job_link
            }

            # 利於資料庫寫入時的資料驗證，要為了確保不同腳本沒有遺漏欄位，並且格式要正確。
            job_instance = JobModel(**job_data)
            return job_instance
        else:
            return None
