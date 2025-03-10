# import requests
from utils.request_utils import make_request
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
# import time
import pytz
from .base_source import BaseSource
from models.jobs import JobModel

class Source104(BaseSource):
  """客製化個別網站參數url"""
  def source_url(self, keyword, page):
      base_url=f'https://www.104.com.tw'
      # url = base_url+f'/jobs/search/?ro=1&isnew=0&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
      #根據api取得資料
      url = base_url+f'/jobs/search/?ro=1&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
    #   https://www.104.com.tw/jobs/search/?ro=1&kwop=7&keyword=node.js&mode=s&jobsource=2018indexpoc&page=1
      # 不確定是否因為被cloudflare抓到而有限制，而且需要爬蟲錯誤暫停機制，太頻繁也會被擋，但是page仍會繼續計算
      print(url)
      return base_url,url
  """解析soup的規則""" 
  #base_url是為了統一格式
  def parse_source_job(self, base_url, keyword,soup=None, job=None):
      #解析單頁條件查詢結果
      if soup:
          job_list = soup.find_all('div', class_='job-list-container')##改版
          api_url = base_url+f'/jobs/search/api/jobs?jobsource=2018indexpoc&keyword={keyword}&kwop=7&mode=s&order=15&page=1&pagesize=20&ro=1'
          data=make_request(api_url).json()
          total_count=data.get('metadata').get("pagination").get("total")
          return {
              "job_list": job_list,
              "total_count": total_count
          }
      #解析個別工作資訊框以及其個別頁面結果
      elif job:
          #分析個別工作資訊框(可考量都從個別頁面取得結果)
          job_title = job.find('a', class_='info-job__text').text.strip()
          job_link = job.find('a', class_='info-job__text')['href']
          company_name = job.find('a', class_='info-company__text').text.strip()
          industry = job.find('span', class_='info-company-addon-type').text.strip()
          job_desc = job.find('div', class_='info-description').text.strip()  # 工作描述，要完整就要換地方爬
          job_exp = job.find('a', href=lambda x: x and 'jobexp' in x).text.strip()

          job_salary_element = job.find('a', attrs={'data-gtm-joblist': lambda x: x and x.startswith('職缺-薪資')})
          if job_salary_element and job_salary_element.text:
              job_salary = job_salary_element.text
          else:
              job_salary = None
              print("警告: 非月薪年薪制。")

          people = job.find('a', class_='action-apply__range').text.strip()[:-2].rstrip('人').strip()
          place = job.find('span', class_='info-tags__text').text.strip()
          
          #分析個別工作頁面結果(更詳細結果)：透過API
          data=make_request(job_link).json()
          #   job_title=data["header"]["jobName"]
          #   company_name=data["header"]["custName"]
          #   job_exp=data["data"]["condition"]["workExp"]

          # 使用 get 方法安全獲取值，並提供默認值
          job_info = [item.get('description') for item in data.get("data", {}).get("condition", {}).get("specialty", [])]
          job_condition = data.get("data", {}).get("condition", {}).get("other")
          update = data.get("data", {}).get("header", {}).get("appearDate")
          job_desc= data.get("data", {}).get("jobDetail", {}).get("jobDescription")

          if update is None:
              print("警告: 找不到更新日期，職缺已關閉。")
          
          job_exp_mapping = {
            "經歷不拘": 0,
            **{f"{i}年以上": i for i in range(1, 11)}  # 自動生成 1~10 年
          }

          """更好被測試"""        
          #要符合JobModel格式(理想上不冗余的命名)
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
            "record_time": datetime.now(pytz.utc).isoformat(),  # Using ISO8601 with timezone info
            "source": "104",
            "keywords": keyword,
            "url": job_link
            }

          #print(job_data)

          #利於資料庫寫入時的資料驗證，要為了確保不同腳本沒有遺漏欄位，並且格式要正確。
          job_instance = JobModel(**job_data)
          return job_instance
      else:
          return None