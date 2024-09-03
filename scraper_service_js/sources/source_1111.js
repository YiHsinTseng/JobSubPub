const cheerio = require('cheerio');
const moment = require('moment');
const { makeRequest } = require('../utils/request_utils');
const BaseSource = require('./base_source');
const JobModel = require('../models/jobs');
const logger = require('../winston');

class Source1111 extends BaseSource {
  sourceUrl(keyword, page) {
    const baseUrl = 'https://www.1111.com.tw';
    const url = `${baseUrl}/search/job?ks=${keyword}&page=${page}`;
    return { baseUrl, url };
  }

  async parseSourceJob(baseUrl, keyword, html = null, job = null) {
    if (html) {
      const $ = cheerio.load(html);
      const jobList = $('div.job-item').toArray();
      const totalCount = parseInt($('div.left p span').text());
      return {
        jobList,
        totalCount,
      };
    } if (job) {
      const $ = cheerio.load(job);
      const jobTitle = $('div.title.position0').text().trim();
      const jobLink = baseUrl + $('div.title.position0 a').attr('href');
      const companyText = $('div.company.organ').text().split('|');
      const companyName = companyText[0].trim();
      const industry = companyText[1].trim();
      const jobDesc = $('p.introduce').text().trim();
      const place = $('div.other a[data-after]').attr('data-after');
      const jobSalary = $('div.other span[data-after]').attr('data-after');
      const people = $('div.people').text().slice(5).trim()
        .replace('人', '')
        .replace('-', '~');
      const updateDateStr = $('div.data').text().trim();
      let update = moment(updateDateStr, 'YYYY/MM/DD').year(moment().year()).format('YYYY-MM-DD');
      if (!moment(update, 'YYYY-MM-DD', false).isValid()) {
        logger.warn('無效日期格式');
        update = null; // pg可接受null
      }

      // 獲取更多工作細節
      const { data: htmlContent2 } = await makeRequest(jobLink);
      const $2 = cheerio.load(htmlContent2);
      const jobSkill = $2('div.content_items.job_skill div.body_2.description_info');
      let jobInfo = [];
      try {
        jobInfo = jobSkill.find('span.job_info_title:contains("電腦專長：")').next().find('a').map((i, el) => $(el).text().trim())
          .get();
      } catch (e) {
        jobInfo = null;
      }

      let jobCondition = null;
      try {
        jobCondition = jobSkill.find('div.job_info_title:contains("附加條件：")').next().find('div.ui_items_group').text()
          .trim();
      } catch (e) {
        jobCondition = null;
      }

      let jobExp = null;
      try {
        jobExp = jobSkill.find('span.job_info_title:contains("工作經驗：")').next().text().trim();
      } catch (e) {
        jobExp = null;
      }

      const jobInstance = new JobModel({
        title: jobTitle,
        companyName,
        industry,
        experience: jobExp,
        description: jobDesc,
        salary: jobSalary,
        applicants: people,
        location: place,
        updateDate: update,
        recordTime: moment().format('YYYY-MM-DD HH:mm:ss'),
        source: '1111',
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

module.exports = Source1111;
