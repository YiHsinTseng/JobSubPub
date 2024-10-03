require('dotenv').config();
const jwt = require('jsonwebtoken');
const cron = require('node-cron');
const { publishMessage } = require('../configs/mqttClient');

const { getUsersFilteredJobs,getUsersSubscriptionConditionsPaginated } =require('./batchQuery')

const { PASSPORT_SECRET, JWT_EXPIRES_IN, MQTT_TOPIC } = process.env;

function generateToken (user_id) {
  return jwt.sign({ user_id }, PASSPORT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

function publishFilteredJobsForUsers(usersFilteredJobs){
  usersFilteredJobs.forEach(({
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
}

async function processUserJobPushes(usersConditions,START_TIME) {
  //外部停止條件
  if (usersConditions === 'end') {
    console.log('Processing completed');
    console.log('Processing time:', new Date() - START_TIME);
    return;
  }
  //一批推送
  try {
    const usersFilteredJobs = await getUsersFilteredJobs(usersConditions);
    publishFilteredJobsForUsers(usersFilteredJobs)

  } catch (error) {
    console.error('Error while processing conditions:', error);
  }
}

async function processBatchUserJobs() {
  let offset = 0;
  const limit = 5000;
  let usersSubscriptionConditions;
  const START_TIME = new Date();
  while (true) {
    //批量拉取訂閱條件
    usersSubscriptionConditions = await getUsersSubscriptionConditionsPaginated(offset, limit);
    offset += limit;
    if (usersSubscriptionConditions.length === 0) {
      processUserJobPushes('end',START_TIME);
      break;
    }
    await processUserJobPushes(usersSubscriptionConditions);
  }
}

//定時推播(UTC時間)與人為介入

function setupCronJobs() {
  const PUBLISH_CRON_TIME=process.env.PUBLISH_CRON_TIME
  cronJobs = cron.schedule(PUBLISH_CRON_TIME, () => {
    console.log('Running scheduled job at', new Date());
    processBatchUserJobs();
  }, { scheduled: true });
  return cronJobs
}

function startCronJobs() {
  if (cronJobs) {
    cronJobs.start();
    console.log('Scheduled job started.');
  } else {
    console.log('Scheduled job is not defined.');
  }
}

function stopCronJobs() {
  if (cronJobs) {
    cronJobs.stop();
    console.log('Scheduled job stopped.');
  } else {
    console.log('Scheduled job is not defined.');
  }
}

module.exports = {
  processBatchUserJobs,
  setupCronJobs,
  startCronJobs,
  stopCronJobs,
};
