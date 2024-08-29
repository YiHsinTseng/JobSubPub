require('dotenv').config();
const jwt = require('jsonwebtoken');
const cron = require('node-cron');
const { publishMessage } = require('../configs/mqttClient');
const { pool } = require('../configs/dbConfig');
const { condGen } = require('../utils/jobCondGen');
const { getDate } = require('../utils/dateUtils');

// const { getSubscriptionConditions } = require('./subs'); //耦合

const { PASSPORT_SECRET, JWT_EXPIRES_IN, MQTT_TOPIC } = process.env;

let start = null;

// 批量抓取訂閱條件
const getSubscriptionConditions = async (offset = 0, limit = 100) => {
  try {
    const query = `
      SELECT user_id, industries, job_info 
      FROM job_subscriptions 
      ORDER BY id 
      LIMIT $1 OFFSET $2
    `;
    const result = await pool.query(query, [limit, offset]);
    return result.rows.map((row) => ({
      user_id: row.user_id,
      industries: row.industries,
      job_info: row.job_info,
    }));
  } catch (error) {
    console.error('Error querying job_subscriptions table:', error);
    return [];
  }
};

// 批量處理查詢(有userid)
const filterJobs = async (conditions) => {
  try {
    const conditionStrings = conditions.map((cond) => {
      const { user_id } = cond;
      const { industries, job_info } = cond;
      const conditionsArray = condGen(cond);
      console.log(`(${conditionsArray.join(' AND ')})`);
      return {
        user_id,
        conditionString: `(${conditionsArray.join(' AND ')})`,
        sub: { industries, job_info },
      };
    });

    const results = await Promise.all(conditionStrings.map(async ({ user_id, conditionString, sub }) => {
      // const query = `
      //   SELECT Count("industry") AS count
      //   FROM jobs
      //   WHERE ${conditionString}
      // `;
      const query = `
        WITH JobCounts AS (
          SELECT 
            COUNT(*) AS total_count,
            COUNT(CASE WHEN DATE(update_date) = CURRENT_DATE THEN 1 END) AS today_count
          FROM jobs
          WHERE ${conditionString}
        )
        SELECT 
          total_count,
          today_count
        FROM JobCounts
      `;
      const result = await pool.query(query);
      // return { user_id, count: result.rows[0].count, sub };
      const options = {
        timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
      };
      return {
        user_id, count: result.rows[0].total_count, update: result.rows[0].today_count, sub, queryDate: getDate(),
      };
    }));

    return results;
  } catch (error) {
    console.error('Error querying jobs table:', error);
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
      user_id, count, update, sub, queryDate,
    }) => {
      const message = JSON.stringify({
        authToken: generateToken(user_id),
        user_id,
        data: {
          count, update, sub, queryDate,
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
