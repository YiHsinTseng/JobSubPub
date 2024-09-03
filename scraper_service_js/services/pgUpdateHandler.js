const path = require('path');
const fs = require('fs');
const { Client } = require('pg');
require('dotenv').config();

const logger = require('../winston');

const createClient = () => {
  const client = new Client({
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  });

  return client;
};

const connectClient = async (client) => {
  try {
    await client.connect();
    logger.info('Connected to PostgreSQL', { source: 'db' });
    await createTables(client);
  } catch (err) {
    logger.error('Connection error', err.stack);
  }
};

const createTable = async (client, filePath) => {
  const sql = fs.readFileSync(path.resolve(__dirname, filePath), 'utf8');
  try {
    await client.query(sql);
    logger.info(`Table created or already exists from ${filePath}`, { source: 'db' });
  } catch (err) {
    logger.error(`Error creating table from ${filePath}:`, err);
  }
};

const createTriggerAndLog = async (client) => {
  const createTriggerLogSQL = fs.readFileSync(path.resolve(__dirname, '../../postgres_db/create_trigger_log.sql'), 'utf8');
  const createTriggerSQL = fs.readFileSync(path.resolve(__dirname, '../../postgres_db/create_act_pub_trigger.sql'), 'utf8');
  try {
    await client.query(createTriggerLogSQL);
    logger.info('Trigger log table created or already exists.', { source: 'db' });
    await client.query(createTriggerSQL);
    logger.info('Activation publication trigger created or already exists.', { source: 'db' });
  } catch (err) {
    logger.error('Error creating triggers:', err);
  }
};

const createTables = async (client) => {
  try {
    await createTable(client, '../../postgres_db/create_jobs.sql');
    await createTable(client, '../../postgres_db/create_job_subs.sql');
    await createTable(client, '../../postgres_db/create_id_subs.sql');
    await createTable(client, '../../postgres_db/create_act_pub_channel.sql');
    await createTriggerAndLog(client);
    logger.info('All tables and triggers created successfully.', { source: 'db' });
  } catch (err) {
    logger.error('Error creating tables:', err);
  }
};

const insertJobsIntoPostgres = async (client, jobs) => {
  const insertJobsSQL = fs.readFileSync(path.resolve(__dirname, '../../postgres_db/insert_jobs_js.sql'), 'utf8');
  try {
    for (const job of jobs) {
      await client.query(insertJobsSQL, [
        job.title,
        job.company_name,
        job.industry,
        job.experience,
        job.description,
        JSON.stringify(job.requirements),
        job.additional_conditions,
        job.salary,
        job.people,
        job.location,
        job.update_date,
        job.record_time,
        job.source,
        job.keywords,
        job.url,
      ]);
    }
    logger.info(`Successfully inserted ${jobs.length} job(s) into PostgreSQL.`, { source: 'db' });
  } catch (err) {
    logger.error('Error inserting data into PostgreSQL:', err);
  }
};

module.exports = { createClient, connectClient, insertJobsIntoPostgres };
