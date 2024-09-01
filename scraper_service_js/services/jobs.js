const fs = require('fs');
const { format } = require('date-fns');
const { makeRequest } = require('../utils/request_utils');
const PostgresHandler = require('./pgUpdateHandler');

const loadState = (stateFile, currentDateString) => {
  try {
    const data = fs.readFileSync(stateFile, 'utf-8');
    const state = JSON.parse(data);
    const fileDate = state.date;

    if (fileDate === currentDateString) {
      return state;
    }
    return {
      date: currentDateString, page: 1, inPageCount: 0, jobsCount: 0,
    };
  } catch (err) {
    return {
      date: currentDateString, page: 1, inPageCount: 0, jobsCount: 0,
    };
  }
};

const saveState = (stateFile, currentDateString, page, totalCount, inPageCount, jobsCount) => {
  const state = {
    date: currentDateString, page, totalCount, inPageCount, jobsCount,
  };
  fs.writeFileSync(stateFile, JSON.stringify(state));
};

const searchJobs = async (source, keyword, stateFile = `./data/save_${source.constructor.name}.json`) => {
  const pgClient = PostgresHandler.createClient();
  await PostgresHandler.connectClient(pgClient);

  const currentDateString = format(new Date(), 'yyyyMMdd');
  const jobs = [];
  const state = loadState(stateFile, currentDateString);
  let totalCount = 0;
  let failedJobsCount = 0;
  let { page, inPageCount, jobsCount } = state;
  const startTime = Date.now();

  while (true) {
    const { baseUrl, url } = source.sourceUrl(keyword, page);
    try {
      const response = await makeRequest(url);
      const html = response.data;

      const { jobList, totalCount: totalCountNum } = await source.parseSourceJob(baseUrl, keyword, html, null);
      totalCount = totalCountNum;
      let remainingCount = totalCount - jobsCount - jobs.length - failedJobsCount;
      if (remainingCount <= 0) break;

      const pageJobs = [];
      for (const job of jobList) {
        try {
          const jobInstance = await source.parseSourceJob(baseUrl, keyword, null, job);
          const jobDict = jobInstance.toDict();
          jobs.push(jobDict);
          pageJobs.push(jobDict);
          inPageCount += 1;
        } catch (e) {
          console.error(`解析職缺資訊失敗: ${e}`);
          failedJobsCount += 1;
          continue;
        }
      }

      await PostgresHandler.insertJobsIntoPostgres(pgClient, pageJobs);
      jobsCount += pageJobs.length;
      saveState(stateFile, currentDateString, page, totalCount, inPageCount, jobsCount);
      page += 1;

      remainingCount = totalCount - jobsCount - jobs.length - failedJobsCount;
      console.log(`已獲取職缺數量：${jobsCount}, 剩餘需要處理的數量：${remainingCount}, 跳過處理數量:${failedJobsCount}`);
    } catch (e) {
      console.error(`請求失敗: ${e}`);
      continue;
    }
  }

  const endTime = Date.now();
  const elapsedTime = (endTime - startTime) / 1000;
  console.log(`搜尋耗時: ${elapsedTime.toFixed(2)} 秒`);

  return { totalCount, jobs };
};

module.exports = { searchJobs };
