# import requests
from utils.request_utils import make_request
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
# import time
import pytz
from .base_source import BaseSource
from models.jobs import JobModel

class Source104(BaseSource):
  def source_url(self, keyword, page):
      base_url=f'https://www.104.com.tw'
      # url = base_url+f'/jobs/search/?ro=1&isnew=0&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
      #根據api取得資料
      url = base_url+f'/jobs/search/?ro=1&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
    #   https://www.104.com.tw/jobs/search/?ro=1&kwop=7&keyword=node.js&mode=s&jobsource=2018indexpoc&page=1
      # 不確定是否因為被cloudflare抓到而有限制，而且需要爬蟲錯誤暫停機制，太頻繁也會被擋，但是page仍會繼續計算
      print(url)
      return base_url,url

  #base_url是為了統一格式
  def parse_source_job(self, base_url, keyword,soup=None, job=None):
      if soup:
          job_list = soup.find_all('div', class_='job-list-container')##改版
          api_url = base_url+f'/jobs/search/api/jobs?jobsource=2018indexpoc&keyword={keyword}&kwop=7&mode=s&order=15&page=1&pagesize=20&ro=1'
          data=make_request(api_url).json()
          total_count=data.get('metadata').get("pagination").get("total")
          return {
              "job_list": job_list,
              "total_count": total_count
          }
      elif job:
          job_title = job.find('a', class_='info-job__text').text.strip()
          job_link = job.find('a', class_='info-job__text')['href']
          company_name = job.find('a', class_='info-company__text').text.strip()
          industry = job.find('span', class_='info-company-addon-type').text.strip()
          job_desc = job.find('div', class_='info-description').text.strip()  # 工作描述，要完整就要換地方爬
          job_exp = job.find('a', href=lambda x: x and 'jobexp' in x).text.strip()
          try:
            job_salary = job.find('a', attrs={'data-gtm-joblist': lambda x: x and x.startswith('職缺-薪資')}).text
          except:
            job_salary = None
          people = job.find('a', class_='action-apply__range').text.strip()[:-2].rstrip('人').strip()
          place = job.find('span', class_='info-tags__text').text.strip()
         
          data=make_request(job_link).json()
          #   job_title=data["header"]["jobName"]
          #   company_name=data["header"]["custName"]
          #   job_exp=data["data"]["condition"]["workExp"]
          job_info=[item['description'] for item in data["data"]["condition"]["specialty"]]
          job_condition= data["data"]["condition"]["other"]
          update= data["data"]["header"]["appearDate"]

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
                source="104",
                keywords=keyword,
                url=job_link,
                requirements=job_info,
                additional_conditions=job_condition
            )
          return job_instance
      else:
          return None