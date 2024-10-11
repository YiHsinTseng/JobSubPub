const { pool } = require('../configs/dbConfig');
const AppError = require('../utils/appError');

const getSubConditions = async (user_id) => {
  try {
    const query = 'SELECT industries, job_info, exclude_job_title FROM job_subscriptions WHERE user_id = $1';
    const result = await pool.query(query, [user_id]);

    if (result.rows.length === 0) {
      return { industries: [], job_info: [], exclude_job_title: [] };
    }

    const row = result.rows[0];
    const Industries = row.industries;
    const JobInfo = row.job_info;
    const ExcludeJobTitle = row.exclude_job_title;

    return {
      industries: Industries,
      job_info: JobInfo,
      exclude_job_title: ExcludeJobTitle,
    };
  } catch (err) {
    console.error('查詢錯誤:', err);
    throw err;
  }
};

const addSubConditions = async (user_id, sub, exclude) => {
  const checkQuery = 'SELECT COUNT(*) FROM job_subscriptions WHERE user_id = $1';

  const values = [user_id]; // 初始化值數組
  const { rows } = await pool.query(checkQuery, values);

  const fields = [...Object.keys(sub), Object.keys(exclude)]; // 獲取動態字段，都是要存到欄位名
  // 要不要保留Exclude
  const setClauseString = fields.map((field) => `${field} = EXCLUDED.${field}`).join(', ');

  const data = { sub, exclude };// 但是轉成參數
  Object.values(data).flatMap((item) => Object.values(item)).forEach((value) => {
    values.push(JSON.stringify(value)); // 逐個推送元素
  });

  // 如果exclude的資料格式怎樣設計
  const insertQuery = `
  INSERT INTO job_subscriptions (user_id, ${fields.join(', ')}, created_at)
  VALUES ($1, ${fields.map((_, i) => `$${i + 2}::jsonb`).join(', ')}, NOW())
  ON CONFLICT (user_id) DO UPDATE 
  SET ${setClauseString}, created_at = NOW();
`;

  const count = parseInt(rows[0].count, 10);
  if (count > 0) {
    await pool.query(insertQuery, values);
    console.log('Record updated successfully');
  } else {
    await pool.query(insertQuery, values);
    console.log('Record inserted successfully');
  }
};

const addSubscribedJob = async (user_id, job_id) => {
  const query = `
    INSERT INTO subscriptions_jobs (user_id, job_id)
    VALUES ($1, $2)
    ON CONFLICT (user_id, job_id) DO NOTHING
  `;

  try {
    await pool.query(query, [user_id, job_id]);
    console.log(`Job ${job_id} has been subscribed for user ${user_id}.`);
  } catch (error) {
    throw new Error('Error adding subscribed job:', error);
  }
};

const deleteSubscribedJob = async (user_id, job_id) => {
  const query = `
    DELETE FROM subscriptions_jobs
    WHERE user_id = $1 AND job_id = $2
  `;

  const res = await pool.query(query, [user_id, job_id]);
  try {
    if (res.rowCount > 0) {
      console.log(`Job ${job_id} has been unsubscribed for user ${user_id}.`);
    } else {
      throw new Error(`No subscription found for job ${job_id} and user ${user_id}.`);
    }
  } catch (error) {
    throw new Error('Error deleting subscribed job:', error);
  }
};

const addSubscribedCompany = async (user_id, company_name) => {
  const query = `
    INSERT INTO subscriptions_companies (user_id, company_name)
    VALUES ($1, $2)
    ON CONFLICT (user_id, company_name) DO NOTHING
  `;

  try {
    await pool.query(query, [user_id, company_name]);
    console.log(`Company ${company_name} has been subscribed for user ${user_id}.`);
  } catch (error) {
    throw new Error('Error adding subscribed company:', error);
  }
};

const deleteSubscribedCompany = async (user_id, company_name) => {
  const query = `
  DELETE FROM subscriptions_companies
  WHERE user_id = $1 AND company_name = $2
`;

  try {
    const res = await pool.query(query, [user_id, company_name]);
    if (res.rowCount > 0) {
      console.log(`Company ${company_name} has been unsubscribed for user ${user_id}.`);
    } else {
      const errorDetail = `No subscription found for compay ${company_name} and user ${user_id}.`;
      console.error(errorDetail);
      throw new AppError(404, `No subscription found for compay ${company_name}.`, errorDetail);
    }
  } catch (error) {
    throw new AppError(error.statusCode, `Error removing subscribed company: ${error.message}`);
  }
};

const updateJobChannel = async (job_id, user_id) => {
  try {
    const query = `
    INSERT INTO job_id_channel (job_id, user_ids)
    VALUES ($1, to_jsonb(ARRAY[$2]::text[]))
    ON CONFLICT (job_id)
    DO UPDATE 
    SET user_ids = COALESCE(job_id_channel.user_ids, '[]'::jsonb) || to_jsonb(ARRAY[$2]::text[]);
    `;

    const result = await pool.query(query, [job_id, user_id]);

    if (result.rowCount > 0) {
      console.log(`User ID ${user_id} added to job ID ${job_id}`);
    } else {
      console.log(`Job ID ${job_id} not found.`);
    }
  } catch (error) {
    console.error('Error updating user_ids:', error);
  }
};

const deleteJobChannel = async (job_id, user_id) => {
  try {
    const query = `
      UPDATE job_id_channel
      SET user_ids = (
        SELECT jsonb_agg(elems)
        FROM jsonb_array_elements(user_ids) elems
        WHERE elems != to_jsonb($2::text)
      )
      WHERE job_id = $1
      AND user_ids @> to_jsonb(ARRAY[$2]::text[]);
    `;

    const result = await pool.query(query, [job_id, user_id]);

    if (result.rowCount > 0) {
      console.log(`User ID ${user_id} removed from job ID ${job_id}`);
    } else {
      console.log(`Job ID ${job_id} not found or User ID ${user_id} was not subscribed.`);
    }
  } catch (error) {
    console.error('Error deleting user_id:', error);
  }
};

const updateCompanyChannel = async (company_name, user_id) => {
  try {
    const query = `
    INSERT INTO company_name_channel (company_name, user_ids)
    VALUES ($1, to_jsonb(ARRAY[$2]::text[]))
    ON CONFLICT (company_name)
    DO UPDATE 
    SET user_ids = COALESCE(company_name_channel.user_ids, '[]'::jsonb) || to_jsonb(ARRAY[$2]::text[]);
    `;

    const result = await pool.query(query, [company_name, user_id]);

    if (result.rowCount > 0) {
      console.log(`User ID ${user_id} added to company ${company_name}`);
    } else {
      console.log(`Company ${company_name} not found.`);
    }
  } catch (error) {
    console.error('Error updating user_ids:', error);
  }
};

const deleteCompanyChannel = async (company_name, user_id) => {
  try {
    const query = `
      UPDATE company_name_channel
      SET user_ids = (
        SELECT jsonb_agg(elems)
        FROM jsonb_array_elements(user_ids) elems
        WHERE elems != to_jsonb($2::text)
      )
      WHERE company_name = $1
      AND user_ids @> to_jsonb(ARRAY[$2]::text[]);
    `;

    const result = await pool.query(query, [company_name, user_id]);

    if (result.rowCount > 0) {
      console.log(`User ID ${user_id} removed from company ${company_name}`);
    } else {
      console.log(`Company ${company_name} not found or User ID ${user_id} was not subscribed.`);
    }
  } catch (error) {
    console.error('Error deleting user_id:', error);
  }
};

const createSubscribedEntities = async (user_id) => {
  const query = `SELECT 
    jsonb_build_object(
        'job_ids', array_agg(DISTINCT sj.job_id), 
        'company_names', array_agg(DISTINCT sc.company_name)
    ) AS subscriptions
  FROM 
      users u
  LEFT JOIN subscriptions_jobs sj ON u.user_id = sj.user_id
  LEFT JOIN subscriptions_companies sc ON u.user_id = sc.user_id
  WHERE 
      u.user_id = $1
  GROUP BY 
      u.user_id;
  `;

  try {
    const result = await pool.query(query, [user_id]);
    if (result.rowCount > 0) {
      return result.rows[0];
    }
    return { subscriptions: { job_ids: [], company_names: [] } };
  } catch (error) {
    console.error('Error fetching user subscriptions:', error);
    throw new Error('Database query failed');
  }
};

module.exports = {
  getSubConditions,
  addSubConditions,
  addSubscribedJob,
  deleteSubscribedJob,
  addSubscribedCompany,
  deleteSubscribedCompany,
  createSubscribedEntities,
  updateJobChannel,
  deleteJobChannel,
  updateCompanyChannel,
  deleteCompanyChannel,
};
