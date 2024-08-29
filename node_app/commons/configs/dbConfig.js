require('dotenv').config(); // 加载环境变量
const { Pool } = require('pg');

// const pool = new Pool({
//   host: 'localhost',
//   // database: 'mock_jobs',
//   database: 'jobs',
//   user: 'test',
//   password: 'test',
// });

// const mock_pool = new Pool({
//   host: 'localhost',
//   database: 'mock_jobs',
//   user: 'test',
//   password: 'test',
// });

const pool = new Pool({
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

const mock_pool = new Pool({
  host: process.env.DB_HOST,
  database: process.env.MOCK_DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

module.exports = { pool, mock_pool };
