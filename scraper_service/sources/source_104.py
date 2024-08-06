# import requests
from utils.request_utils import make_request
from bs4 import BeautifulSoup
from datetime import datetime
import time
from .base_source import BaseSource
from models.jobs import JobModel

class Source104(BaseSource):
  def soruce_url(self, keyword, page):
      base_url=f'https://www.104.com.tw'
      # url = base_url+f'/jobs/search/?ro=1&isnew=0&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
      url = base_url+f'/jobs/search/?ro=1&kwop=7&keyword={keyword}&mode=s&jobsource=2018indexpoc&page={page}'
      return base_url,url

  def parse_source_job(self, base_url, soup=None, job=None):
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

          # 如果找不到會跳出
          # return {
          #     '職缺名稱': job_title,
          #     '公司名稱': company_name,
          #     "產業": industry,
          #     "年資": job_exp,
          #     '職缺描述': job_desc,
          #     '薪資': job_salary,
          #     "應徵人數": people,
          #     "地區": place,
          #     "更新日期": update,
          #     "紀錄時間": datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
          #     "來源": "104",
          #     "職缺網址": job_link,
          #     "工作要求": job_info,
          #     "附加條件":job_condition
          # }
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
                url=job_link,
                requirements=job_info,
                additional_conditions=job_condition
            )
          return job_instance
      else:
          return None

  # def search_jobs(keyword):
  #     jobs = []  # 初始化回傳資料
  #     total_count = 0
  #     jump=0
  #     skip= []
  #     page = 1  # 初始化頁面為第1頁
  #     start_time = time.time() 
  #     # keyword=keyword


  #     while True:
        
  #         base_url,url=soruce_url(keyword,page)
          
  #         try:
  #             html_content=make_request(url).text
  #             soup = BeautifulSoup(html_content, 'html.parser')
              
  #             joblist_dict=parse_source_job(base_url,soup=soup)
  #             job_list = joblist_dict["job_list"]
  #             total_count = joblist_dict["total_count"]
  #             remaining_count = total_count - len(jobs)-jump
              
  #             print(f'已獲取職缺數量：{len(jobs)}, 剩餘需要處理的數量：{remaining_count},跳過處理數量:{jump}')
  #             print("=> Fetch ",url)
  #             print("->",keyword)

  #             # 如果剩余职位数量小于每页的最大数量，就不需要再继续翻页了
  #             # if remaining_count <= len(job_list):
  #             if remaining_count <= 0:
  #                 break

  #             for job in job_list:
  #                 try:
  #                     job_dict=parse_source_job(base_url,job=job)
        
  #                     jobs.append({
  #                         '職缺名稱': job_dict['職缺名稱'],
  #                         '公司名稱': job_dict['公司名稱'],
  #                         "產業": job_dict["產業"],
  #                         "年資": job_dict["年資"],
  #                         '職缺描述': job_dict["職缺描述"],
  #                         "工作要求": job_dict["工作要求"],
  #                         "附加條件": job_dict["附加條件"],
  #                         '薪資': job_dict["薪資"],
  #                         "應徵人數": job_dict["應徵人數"],
  #                         "地區": job_dict["地區"],
  #                         "更新日期": job_dict["更新日期"],
  #                         "紀錄時間": job_dict["紀錄時間"],
  #                         "來源": job_dict["來源"],
  #                         "關鍵字": keyword,
  #                         "職缺網址": job_dict["職缺網址"]
  #                     })
  #                 except Exception as e:
  #                     print(f'解析職缺資訊失敗: {e}')
  #                     jump+=1
  #                     skip.append(url)
  #                     continue  # 如果解析失敗，跳過當前職缺的解析
              
              
  #             page += 1  # 更新頁面參數

  #         except Exception as e:
  #             print(f'請求失敗: {e}')
  #             total_count = 0
  #             continue  # 發生異常時繼續執行後續
          
  #     remaining_count = total_count - len(jobs)-jump
  #     print(f'已獲取職缺數量：{len(jobs)}, 剩餘需要處理的數量：{remaining_count},跳過處理數量:{jump}')     
  #     end_time = time.time()  # 結束計時
  #     elapsed_time = end_time - start_time
  #     print(f'搜尋耗時: {elapsed_time:.2f} 秒')
      
  #     df = pd.DataFrame(jobs)
  #     current_date_time = datetime.now()
  #     date_string = current_date_time.strftime("%Y%m%d")
  #     df.to_csv(f'data/jobs104_{date_string}_node.csv', header=True,index=False)
  #     return total_count, jobs ,skip

# 搜尋並獲取結果

# total_count, jobs = search_jobs('node.js') 
# df = pd.DataFrame(jobs)
# print('搜尋結果職缺總數：', total_count)
# result = df.head(total_count)
# print(result)






# %%
