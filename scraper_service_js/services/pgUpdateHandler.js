const path = require('path');
const fs = require('fs');
const { Client } = require('pg');
require('dotenv').config();

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
    console.log('Connected to PostgreSQL');
    await createTables(client);
  } catch (err) {
    console.error('Connection error', err.stack);
  }
};

const createTable = async (client, filePath) => {
  const sql = fs.readFileSync(path.resolve(__dirname, filePath), 'utf8');
  try {
    await client.query(sql);
    console.log(`Table created or already exists from ${filePath}`);
  } catch (err) {
    console.error(`Error creating table from ${filePath}:`, err);
  }
};

const createTriggerAndLog = async (client) => {
  const createTriggerLogSQL = fs.readFileSync(path.resolve(__dirname, '../../postgres_db/create_trigger_log.sql'), 'utf8');
  const createTriggerSQL = fs.readFileSync(path.resolve(__dirname, '../../postgres_db/create_act_pub_trigger.sql'), 'utf8');
  try {
    await client.query(createTriggerLogSQL);
    console.log('Trigger log table created or already exists.');
    await client.query(createTriggerSQL);
    console.log('Activation publication trigger created or already exists.');
  } catch (err) {
    console.error('Error creating triggers:', err);
  }
};

const createTables = async (client) => {
  try {
    await createTable(client, '../../postgres_db/create_jobs.sql');
    await createTable(client, '../../postgres_db/create_job_subs.sql');
    await createTable(client, '../../postgres_db/create_id_subs.sql');
    await createTable(client, '../../postgres_db/create_act_pub_channel.sql');
    await createTriggerAndLog(client);
    console.log('All tables and triggers created successfully.');
  } catch (err) {
    console.error('Error creating tables:', err);
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
    console.log(`Successfully inserted ${jobs.length} job(s) into PostgreSQL.`);
  } catch (err) {
    console.error('Error inserting data into PostgreSQL:', err);
  }
};

module.exports = { createClient, connectClient, insertJobsIntoPostgres };
