const { pool } = require('../configs/dbConfig');

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

const getJobSubs = async (user_id) => {
  try {
    // 使用 SQL 查詢，假設你的表名為 job_id_subscription
    const query = 'SELECT industries, job_info FROM job_subscriptions WHERE user_id = $1';
    const result = await pool.query(query, [user_id]);

    if (result.rows.length === 0) {
      return { industries: [], job_info: [] };
    }

    // 取出查詢結果中的 JSONB 欄位
    const row = result.rows[0];
    const Industries = row.industries;
    const JobInfo = row.job_info;

    // 返回 JSON 格式
    return {
      industries: Industries,
      job_info: JobInfo,
    };
  } catch (err) {
    console.error('查詢錯誤:', err);
    throw err;
  }
};

const getIdSubs = async (user_id) => {
  try {
    // 使用 SQL 查詢，假設你的表名為 job_id_subscription
    const query = 'SELECT job_ids, company_names FROM job_id_subscriptions WHERE user_id = $1';
    const result = await pool.query(query, [user_id]);

    if (result.rows.length === 0) {
      return { job_ids: [], company_names: [] };
    }

    // 取出查詢結果中的 JSONB 欄位
    const row = result.rows[0];
    const jobIds = row.job_ids;
    const companyNames = row.company_names;

    // 返回 JSON 格式
    return {
      job_ids: jobIds,
      company_names: companyNames,
    };
  } catch (err) {
    console.error('查詢錯誤:', err);
    throw err;
  }
};

const addJobSubs = async (user_id, sub) => {
  const checkQuery = 'SELECT COUNT(*) FROM job_subscriptions WHERE user_id = $1';
  const insertQuery = `
    INSERT INTO job_subscriptions (user_id, industries, job_info, created_at)
    VALUES ($1, $2::jsonb, $3::jsonb, NOW())
    ON CONFLICT (user_id) DO UPDATE 
    SET industries = EXCLUDED.industries,
        job_info = EXCLUDED.job_info,
        created_at = EXCLUDED.created_at;
  `;

  const values = [
    user_id,
    JSON.stringify(sub.industries),
    JSON.stringify(sub.job_info),
  ];

  const { rows } = await pool.query(checkQuery, [user_id]);
  if (parseInt(rows[0].count) > 0) {
    // Update existing record
    await pool.query(insertQuery, values);
    console.log('Record updated successfully');
  } else {
    // Insert new record
    await pool.query(insertQuery, values);
    console.log('Record inserted successfully');
  }
};

const addIdSubs = async (user_id, sub) => {
  const query = `
    INSERT INTO job_id_subscriptions (user_id, job_ids, company_names, created_at, updated_at)
    VALUES ($1, $2::jsonb, $3::jsonb, NOW(), NOW())
    ON CONFLICT (user_id)
    DO UPDATE SET
      job_ids = (
        SELECT jsonb_agg(elem) 
        FROM (
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(job_id_subscriptions.job_ids) elem
          UNION
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(EXCLUDED.job_ids) elem
        ) subquery
      ),
      company_names = (
        SELECT jsonb_agg(elem) 
        FROM (
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(job_id_subscriptions.company_names) elem
          UNION
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(EXCLUDED.company_names) elem
        ) subquery
      ),
      updated_at = NOW();
  `;

  const channelInsertQuery = `
    INSERT INTO job_id_channel (job_id, user_ids)
    VALUES ($1, jsonb_build_array($2::text))
    ON CONFLICT (job_id)
    DO UPDATE SET
      user_ids = (
        SELECT jsonb_agg(elem) 
        FROM (
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(job_id_channel.user_ids) elem
          UNION
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(EXCLUDED.user_ids) elem
        ) subquery
      );
  `;

  const companyChannelInsertQuery = `
    INSERT INTO company_name_channel (company_name, user_ids)
    VALUES ($1, jsonb_build_array($2::text))
    ON CONFLICT (company_name)
    DO UPDATE SET
      user_ids = (
        SELECT jsonb_agg(elem) 
        FROM (
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(company_name_channel.user_ids) elem
          UNION
          SELECT DISTINCT elem 
          FROM jsonb_array_elements(EXCLUDED.user_ids) elem
        ) subquery
      );
  `;

  const values = [
    user_id,
    JSON.stringify(sub.job_ids),
    JSON.stringify(sub.company_names),
  ];

  try {
    // console.log(query);
    await pool.query(query, values);
    console.log('Insert or update successful');

    // Insert or update job_id_channel
    for (const job_id of sub.job_ids) {
      await pool.query(channelInsertQuery, [job_id, user_id]);
    }

    // Insert or update company_name_channel
    for (const company_name of sub.company_names) {
      await pool.query(companyChannelInsertQuery, [company_name, user_id]);
    }
  } catch (error) {
    console.error('Error adding job id subscriptions:', error);
  }
};

const deleteIdSubs = async (user_id, sub) => {
  const query = `
    UPDATE job_id_subscriptions
    SET
      job_ids = (
        SELECT jsonb_agg(elem)
        FROM (
          SELECT DISTINCT elem
          FROM jsonb_array_elements(job_id_subscriptions.job_ids) elem
          EXCEPT
          SELECT DISTINCT elem
          FROM jsonb_array_elements($2::jsonb) elem
        ) AS subquery
      ),
      company_names = (
        SELECT jsonb_agg(elem)
        FROM (
          SELECT DISTINCT elem
          FROM jsonb_array_elements(job_id_subscriptions.company_names) elem
          EXCEPT
          SELECT DISTINCT elem
          FROM jsonb_array_elements($3::jsonb) elem
        ) AS subquery
      ),
      updated_at = NOW()
    WHERE user_id = $1;
  `;

  const channelDeleteQuery = `
  UPDATE job_id_channel
  SET
    user_ids = (
      SELECT jsonb_agg(elem)
      FROM (
        SELECT DISTINCT elem
        FROM jsonb_array_elements(job_id_channel.user_ids) elem
        EXCEPT
        SELECT DISTINCT elem
        FROM jsonb_array_elements($1::jsonb) elem
      ) AS subquery
    )
  WHERE job_id = $2;
`;

  const companyChannelDeleteQuery = `
    UPDATE company_name_channel
    SET
      user_ids = (
        SELECT jsonb_agg(elem)
        FROM (
          SELECT DISTINCT elem
          FROM jsonb_array_elements(company_name_channel.user_ids) elem
          EXCEPT
          SELECT DISTINCT elem
          FROM jsonb_array_elements($1::jsonb) elem
        ) AS subquery
      )
    WHERE company_name = $2;
  `;

  const values = [
    user_id,
    JSON.stringify(sub.job_ids || []), // Ensure that sub.job_ids is an array or default to empty array
    JSON.stringify(sub.company_names || []), // Ensure that sub.company_names is an array or default to empty array
  ];

  try {
    // console.log(query);
    await pool.query(query, values);
    console.log('delete successful');
    // Delete from job_id_channel
    for (const job_id of sub.job_ids) {
      await pool.query(channelDeleteQuery, [JSON.stringify([user_id]), job_id]);
    }

    // Delete from company_name_channel
    for (const company_name of sub.company_names) {
      await pool.query(companyChannelDeleteQuery, [JSON.stringify([user_id]), company_name]);
    }
  } catch (error) {
    console.error('Error deleting job id subscriptions:', error);
  }
};

module.exports = {
  addJobSubs, addIdSubs, deleteIdSubs, getSubscriptionConditions, getIdSubs, getJobSubs,
};
