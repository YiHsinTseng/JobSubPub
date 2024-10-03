const { pool } = require('../configs/dbConfig');


//硬編碼，要與前端配合
const getJobSubs = async (user_id) => {
  try {
    // 使用 SQL 查詢，假設你的表名為 job_id_subscription
    const query = 'SELECT industries, job_info, exclude_job_title FROM job_subscriptions WHERE user_id = $1';
    const result = await pool.query(query, [user_id]);

    if (result.rows.length === 0) {
      return { industries: [], job_info: [],exclude_job_title:[]};
    }

    // 取出查詢結果中的 JSONB 欄位
    const row = result.rows[0];
    const Industries = row.industries;
    const JobInfo = row.job_info;
    const ExcludeJobTitle = row.exclude_job_title;

    // 返回 JSON 格式
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

//硬編碼?
const addJobSubs = async (user_id, sub,exclude) => {

  const checkQuery = 'SELECT COUNT(*) FROM job_subscriptions WHERE user_id = $1';

  const values = [user_id]; // 初始化值數組
  const { rows } = await pool.query(checkQuery, values);

  const fields = [...Object.keys(sub),Object.keys(exclude)]; // 獲取動態字段，都是要存到欄位名
  //要不要保留Exclude
  const setClauseString = fields.map((field) => `${field} = EXCLUDED.${field}`).join(', '); 

  const data={sub,exclude}//但是轉成參數
  Object.values(data).flatMap(item => Object.values(item)).forEach(value => {
    values.push(JSON.stringify(value)); // 逐個推送元素
  });

  //如果exclude的資料格式怎樣設計
  const insertQuery = `
  INSERT INTO job_subscriptions (user_id, ${fields.join(', ')}, created_at)
  VALUES ($1, ${fields.map((_, i) => `$${i + 2}::jsonb`).join(', ')}, NOW())
  ON CONFLICT (user_id) DO UPDATE 
  SET ${setClauseString}, created_at = NOW();
`;

  if (parseInt(rows[0].count) > 0) {
    await pool.query(insertQuery, values);
    console.log('Record updated successfully');
  } else {
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
  //addJobSubs, addIdSubs, deleteIdSubs, getSubscriptionConditions, getIdSubs, getJobSubs,
  addJobSubs, addIdSubs, deleteIdSubs, getIdSubs, getJobSubs,
};
