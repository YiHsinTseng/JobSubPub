const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');
const moment = require('moment');

const schedule = require('node-schedule');
const logger = require('../winston');
const { sourceLoader } = require('../utils/source_loader');
const JobService = require('../services/jobs');
const {
  JOB_STATUS, JOB_DURATION,
} = require('../metrics');

const searchAndSaveJobs = async (sources, keyword) => {
  let allJobs = [];
  let totalCountAllSources = 0;

  // 多腳本切換（可以優化效率）？不需要並行？
  for (const source of sources) {
    logger.info(`正在處理數據來源: ${source.constructor.name}`);
    const { totalCount, jobs } = await JobService.searchJobs(source, keyword);

    allJobs = allJobs.concat(jobs);
    totalCountAllSources += totalCount;
  }

  const csvWriter = createObjectCsvWriter({
    path: path.join('data', `jobs_${moment().format('YYYYMMDD')}_${keyword}.csv`),
    header: Object.keys(allJobs[0] || {}).map((key) => ({ id: key, title: key })),
  });
  await csvWriter.writeRecords(allJobs);
  return { totalCountAllSources, allJobs };
};

const job = async () => {
  try {
    const sources = await sourceLoader();
    if (sources.length > 0) {
      const keyword = 'node.js'; // 透過 API 修改關鍵字
      const end = JOB_DURATION.startTimer();
      try {
        await searchAndSaveJobs(sources, keyword);
      } finally {
        end(); // 計算 job 執行時間
      }
    }
  } catch (err) {
    logger.error('Error occurred:', { message: err.message, stack: err.stack });
  }
};

const scheduleJob = () => {
  try {
    schedule.scheduleJob('0 9 * * *', job);
    JOB_STATUS.set(1);
  } catch (err) {
    logger.error('Error occurred:', { message: err.message, stack: err.stack });
  }
};

module.exports = { job, scheduleJob };
