const axios = require('axios');
const { promisify } = require('util');
const logger = require('../winston');

const sleep = promisify(setTimeout); // 使 setTimeout 成为返回 Promise 的函数

async function makeRequest(url) {
  if (url.startsWith('https://www.104.com.tw/job/')) {
    const jobId = url.split('/').pop();
    url = `https://www.104.com.tw/job/ajax/content/${jobId}`;
  }
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
    Referer: url,
  };

  await sleep(0.001); // 暂停 0.5 毫秒
  // 使用併發請求104網站不見得比較快，併發2 停0.5 容易觸發429(併發比較容器429)
  // 但個別請求 0.001秒卻沒有觸發429
  try {
    const response = await axios.get(url, { headers });
    logger.info(`Response status code: ${response.status} ${url}`);
    return response;
  } catch (error) {
    logger.error('Request failed:', error.response ? error.response.status : error.message);
    throw error;
  }
}

module.exports = { makeRequest };
