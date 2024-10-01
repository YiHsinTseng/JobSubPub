require('dotenv').config();
const jwt = require('jsonwebtoken');
const cron = require('node-cron');
const { publishMessage } = require('../configs/mqttClient');
const { pool } = require('../configs/dbConfig');
// const { condGen } = require('../utils/jobCondGen');
const { filterJobs } =require('./filterJobs')

const { PASSPORT_SECRET, JWT_EXPIRES_IN, MQTT_TOPIC } = process.env;

let start = null;

// 批量抓取訂閱條件
const getSubscriptionConditions = async (offset = 0, limit = 100) => {
  try {
    const query = `
      SELECT user_id, industries, job_info, exclude_job_title 
      FROM job_subscriptions 
      ORDER BY id 
      LIMIT $1 OFFSET $2
    `;
    const result = await pool.query(query, [limit, offset]);
    return result.rows.map((row) => ({
      user_id: row.user_id,
      industries: row.industries,
      job_info: row.job_info,
      exclude_job_title: row.exclude_job_title,
    }));
  } catch (error) {
    console.error('Error querying job_subscriptions table:', error);
    return [];
  }
};

const generateToken = (user_id) => jwt.sign({ user_id }, PASSPORT_SECRET, { expiresIn: JWT_EXPIRES_IN });

async function processPush(conditions) {
  if (conditions === 'end') {
    console.log('Processing completed');
    console.log('Processing time:', new Date() - start);
    return;
  }
  try {
    const jobResults = await filterJobs(conditions);
    jobResults.forEach(({
      user_id, count, update, sub, exclude, queryDate,
    }) => {
      const message = JSON.stringify({
        authToken: generateToken(user_id),
        user_id,
        data: {
          count, update, sub, exclude, queryDate,
        },
      });
      publishMessage(MQTT_TOPIC, message);
    });
  } catch (error) {
    console.error('Error while processing conditions:', error);
  }
}

async function processJobs() {
  let offset = 0;
  const limit = 5000;
  let subscriptionConditions;
  start = new Date();
  while (true) {
    subscriptionConditions = await getSubscriptionConditions(offset, limit);
    offset += limit;
    if (subscriptionConditions.length === 0) {
      processPush('end');
      break;
    }
    await processPush(subscriptionConditions);
  }
}

let scheduledJob;
function setupScheduledJobs() {
  scheduledJob = cron.schedule('43 4 * * *', () => {
    console.log('Running scheduled job at', new Date());
    processJobs();
  }, { scheduled: true });
}

function startScheduledJob() {
  if (scheduledJob) {
    scheduledJob.start();
    console.log('Scheduled job started.');
  } else {
    console.log('Scheduled job is not defined.');
  }
}

function stopScheduledJob() {
  if (scheduledJob) {
    scheduledJob.stop();
    console.log('Scheduled job stopped.');
  } else {
    console.log('Scheduled job is not defined.');
  }
}

module.exports = {
  processJobs,
  setupScheduledJobs,
  startScheduledJob,
  stopScheduledJob,
};
