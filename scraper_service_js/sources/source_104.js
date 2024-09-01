// const axios = require('axios');
const cheerio = require('cheerio');
const moment = require('moment');
const { makeRequest } = require('../utils/request_utils');
const BaseSource = require('./base_source'); // 假設你有一個 base_source 模塊
const JobModel = require('../models/jobs'); // 假設你有一個 jobs 模塊
const logger = require('../winston'); // 引入 winston 配置

class Source104 extends BaseSource {
  sourceUrl(keyword, page) {
    const baseUrl = 'https://www.104.com.tw';
    const url = `${baseUrl}/jobs/search/?ro=1&kwop=7&keyword=${encodeURIComponent(keyword)}&mode=s&jobsource=2018indexpoc&page=${page}`;
    return { baseUrl, url };
  }

  async parseSourceJob(baseUrl, keyword, html = null, job = null) {
    if (html) {
      const $ = cheerio.load(html);
      const jobList = $('article.b-block--top-bord.job-list-item.b-clearfix.js-job-item').toArray();
      const metaDescription = $('meta[name="description"]').attr('content');
      const totalCount = parseInt(metaDescription.split('－')[1].split(' ')[0], 10);
      return {
        jobList,
        totalCount,
      };
    }

    if (job) {
      const $ = cheerio.load(job);
      const jobTitle = $(job).attr('data-job-name') || '';
      const jobLink = `https:${$(job).find('a.js-job-link').attr('href')}` || '';
      const companyName = $(job).attr('data-cust-name') || '';
      const industry = $(job).attr('data-indcat-desc') || '';
      let jobDesc = $(job).find('p.job-list-item__info').text().trim() || '';
      const jobSalary = $(job).find('span.b-tag--default').text() || '';
      const people = $(job).find('a.b-link--gray.gtm-list-apply').text().slice(0, -2)
        .trim() || '';
      const jobExp = $(job).find('ul.b-list-inline.b-clearfix.job-list-intro.b-content li').eq(1).text() || '';
      const place = $(job).find('ul.b-list-inline.b-clearfix.job-list-intro.b-content li').first().text() || '';

      const jobSalaryText = jobSalary === '遠端工作' ? $(job).find('a.b-tag--default').text() : jobSalary;

      // 獲取更多工作細節
      const response = await makeRequest(jobLink);
      const jobDetails = response.data;
      const jobInfo = (jobDetails.data && jobDetails.data.condition && jobDetails.data.condition.specialty)
        ? jobDetails.data.condition.specialty.map((item) => item.description)
        : [];
      const jobCondition = jobDetails.data && jobDetails.data.condition ? jobDetails.data.condition.other : '';
      jobDesc = jobDetails.data && jobDetails.data.jobDetail ? jobDetails.data.jobDetail.jobDescription : '';

      let update = jobDetails.data.header.appearDate;
      if (!moment(update, 'YYYY-MM-DD', false).isValid()) {
        logger.warn(`無效日期格式:${jobLink}`);// 熱門職缺要深入分析html
        update = null; // pg可接受null
      }

      const jobInstance = new JobModel({
        title: jobTitle,
        companyName,
        industry,
        experience: jobExp,
        description: jobDesc,
        salary: jobSalaryText,
        applicants: people,
        location: place,
        updateDate: update,
        recordTime: moment().format('YYYY-MM-DD HH:mm:ss'),
        source: '104',
        keywords: keyword,
        url: jobLink,
        requirements: jobInfo,
        additionalConditions: jobCondition,
      });

      return jobInstance;
    }

    return null;
  }
}

module.exports = Source104;
