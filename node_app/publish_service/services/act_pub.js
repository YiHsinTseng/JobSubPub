require('dotenv').config(); // 加载环境变量
const { Client } = require('pg');
const { pool } = require('../configs/dbConfig');
const { publishMessage } = require('../configs/mqttClient');

const { MQTT_JOB, MQTT_COMPANY } = process.env;


// 使用獨立客戶端進行 LISTEN
const listenForNotifications = async () => {
  const pgClient = new Client({
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  });

  try {
    await pgClient.connect(); 
    console.log('Connected to PostgreSQL for notifications');

    await pgClient.query(`LISTEN ${MQTT_JOB}`);
    await pgClient.query(`LISTEN ${MQTT_COMPANY}`);
    console.log(`PostgreSQL listening to ${MQTT_JOB} and ${MQTT_COMPANY}`);


    pgClient.on('notification', async (msg) => {
      const { channel, payload } = msg;
      let parsedPayload;
      try {
        parsedPayload = JSON.parse(payload);
        console.log("收到PG消息");
      } catch (error) {
        console.error('Error parsing payload:', error);
        return;
      }

      const channelsConfig = {
        [MQTT_JOB]: {
          tableName: MQTT_JOB,
          queryField: 'job_id',
          queryValue: parsedPayload.job_id,
          mqttTopic: MQTT_JOB,
        },
        [MQTT_COMPANY]: {
          tableName: MQTT_COMPANY,
          queryField: 'company_name',
          queryValue: parsedPayload.company_name,
          mqttTopic: MQTT_COMPANY,
        },
      };

      const config = channelsConfig[channel];
      if (!config) {
        console.warn('Unknown channel:', channel);
        return;
      }

      const { tableName, queryField, queryValue, mqttTopic } = config;
      const userIdsQuery = `
        SELECT user_ids
        FROM ${tableName}
        WHERE ${queryField} = $1
      `;

      try {
        const res = await pool.query(userIdsQuery, [queryValue]);
        if (res.rows.length === 0) {
          console.log(`No users found for ${queryField} ${queryValue}`);
          return;
        }

        const userIds = res.rows[0].user_ids;
        const messages = userIds.map((userId) => JSON.stringify({ user_id: userId, data: parsedPayload }));
        messages.forEach((message) => {
          publishMessage(mqttTopic, message);
        });
      } catch (error) {
        console.error('Error querying or publishing messages:', error);
      }
    });
  } catch (err) {
    console.error('PostgreSQL connection error', err.stack);
  }
};


listenForNotifications();
