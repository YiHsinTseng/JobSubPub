const { pool } = require('../configs/dbConfig');
const { getSubscriptionConditions } = require('./subs');

// 批量抓取訂閱條件
// async function getSubscriptionConditions(offset = 0, limit = 100) {
//   try {
//     const query = `
//       SELECT user_id, industries, job_info
//       FROM job_subscriptions
//       ORDER BY id
//       LIMIT $1 OFFSET $2
//     `;
//     const result = await pool.query(query, [limit, offset]);
//     return result.rows.map((row) => ({
//       user_id: row.user_id,
//       industries: row.industries,
//       job_info: row.job_info,
//     }));
//   } catch (error) {
//     console.error('Error querying job_subscriptions table:', error);
//     return [];
//   }
// }

const condGen = (cond) => {
  const { industries, job_info } = cond; // 給多一點選項？
  let industryCondition = '';
  if (industries && industries.length > 0) {
    industryCondition = `industry IN (${industries.map((v) => `'${v}'`).join(',')})`;
  }
  let job_infoCondition = '';
  if (job_info && job_info.length > 0) { // 修正判斷錯誤
    job_infoCondition = `
    EXISTS (
      SELECT 1
      FROM jsonb_array_elements(job_info) AS elem
      WHERE elem->>0 IN (${job_info.map((v) => `'${v}'`).join(',')})
    )
  `;
  }

  // 聚合所有條件
  const conditionsArray = [];
  if (industryCondition) conditionsArray.push(industryCondition);
  if (job_infoCondition) conditionsArray.push(job_infoCondition);

  return conditionsArray;
};

// 批量處理查詢(有userid)
const filterJobs = async (conditions) => {
  try {
    const conditionStrings = conditions.map((cond) => {
      const { user_id } = cond;
      const { industries, job_info } = cond;
      const conditionsArray = condGen(cond);
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
      return {
        user_id, count: result.rows[0].total_count, update: result.rows[0].today_count, sub,
      };
    }));

    return results;
  } catch (error) {
    console.error('Error querying jobs table:', error);
    return [];
  }
};

// 回傳分頁值(沒有userid)
const getJobs = async (condition, count, limit = 50, offset = 0) => {
  // console.log(condition, count);
  try {
  // 確保 conditions 是一個對象
    if (typeof condition !== 'object' || condition === null) {
      throw new Error('Invalid conditions format');
    }
    const conditionsArray = condGen({ condition }); // 假裝是批量
    // console.log(conditionsArray);

    // 構建最終條件字符串
    const conditionString = conditionsArray.length > 0 ? `(${conditionsArray.join(' AND ')})` : 'TRUE'; // Default to TRUE if no conditions

    // 生成查询
    const query = `
    SELECT *
    FROM jobs
    WHERE ${conditionString}
    ORDER BY update_date DESC
    LIMIT $1 OFFSET $2
  `;
    const result = await pool.query(query, [limit, offset]);

    // return result;
    // 推算總頁數
    const totalItems = count; // 假設 req.count 中帶有總數
    const totalPages = Math.ceil(totalItems / limit);
    const currentPage = Math.floor(offset / limit) + 1;

    return {
      currentPage,
      totalPages,
      totalItems,
      items: result.rows,
    };
  } catch (error) {
    console.error('Error querying jobs table:', error);
    throw new Error('Error querying jobs table');
  }
};

module.exports = {
  getJobs, filterJobs, getSubscriptionConditions, condGen,
};
