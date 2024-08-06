# import requests
from utils.request_utils import make_request
from bs4 import BeautifulSoup
from datetime import datetime
import time
from .base_source import BaseSource
from models.jobs import JobModel

class Source104(BaseSource):
  def source_url(self, keyword, page):
      base_url=f'https://www.104.com.tw'
      # url = base_url+f'/jobs/search/?ro=1&isnew=0&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
      url = base_url+f'/jobs/search/?ro=1&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
      return base_url,url

  def parse_source_job(self, base_url, keyword,soup=None, job=None):
      if soup:
          job_list = soup.find_all('article', class_='b-block--top-bord job-list-item b-clearfix js-job-item')
          total_count = int(soup.find('meta', attrs={'name': 'description'})['content'].split('－')[1].split()[0])
          return {
              "job_list": job_list,
              "total_count": total_count
          }
      elif job:
          job_title = job['data-job-name']  # 工作名稱
          job_link = "https:" + job.find('a', class_='js-job-link').get('href')
          company_name = job['data-cust-name']  # 公司名稱
          industry = job["data-indcat-desc"] 
          job_desc = job.find('p', class_='job-list-item__info').text.strip()  # 工作描述，要完整就要換地方爬
          job_salary = job.find('span', class_='b-tag--default')
          people = job.find("a", class_="b-link--gray gtm-list-apply").text[:-2]
          job_exp= job.find("ul",class_="b-list-inline b-clearfix job-list-intro b-content").find_all("li")[1].text
          place= job.find("ul",class_="b-list-inline b-clearfix job-list-intro b-content").find("li").text
          #update = job.find("span",class_="b-tit__date").text
          update =datetime.strptime(job.find("span",class_="b-tit__date").text.strip(), "%m/%d").replace(year=datetime.now().year).strftime("%Y-%m-%d")

          if job_salary  is not None:
              # 取得元素的文字內容
              job_salary  = job_salary.text
              if(job_salary=="遠端工作"):
                  job_salary  =job.find('a', class_='b-tag--default').text
          else:
              job_salary  =job.find('a', class_='b-tag--default').text
      
          data=make_request(job_link).json()
          job_info=[item['description'] for item in data["data"]["condition"]["specialty"]]
          job_condition= data["data"]["condition"]["other"]
          job_desc= data["data"]["jobDetail"]["jobDescription"]

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
                record_time=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                source="104",
                keywords=keyword,
                url=job_link,
                requirements=job_info,
                additional_conditions=job_condition
            )
          return job_instance
      else:
          return None