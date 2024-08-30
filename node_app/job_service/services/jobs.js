const { pool } = require('../configs/dbConfig');
const { getSubscriptionConditions } = require('./subs');
const { condGen } =require('../utils/jobCondGen')
const { filterJobs } =require('./filterJobs')

// 回傳分頁值(沒有userid)
const getJobs = async (condition, count,date, limit = 50, offset = 0) => {
  // console.log(condition, count);
  try {
  // 確保 conditions 是一個對象
    if (typeof condition !== 'object' || condition === null) {
      throw new Error('Invalid conditions format');
    }
    const {conditionsArray,queryParams} = condGen(condition);
    // console.log(conditionsArray)

    // 構建最終條件字符串
    const conditionString = conditionsArray.length > 0 ? `(${conditionsArray.join(' AND ')})` : 'TRUE'; // Default to TRUE if no conditions

     // 將日期參數加入 queryParams
     queryParams.push(date);

    // 生成查询
  //   const query = `
  //   SELECT *
  //   FROM jobs
  //   WHERE ${conditionString}
  //   AND DATE(update_date) = $3
  //   ORDER BY update_date DESC
  //   LIMIT $1 OFFSET $2
  // `;
      const query = `
      SELECT *
      FROM jobs
      WHERE ${conditionString}
      AND DATE(update_date) = $${queryParams.length}
      ORDER BY update_date DESC
      LIMIT $${queryParams.length + 1}  OFFSET $${queryParams.length + 2} 
    `;

    // const result = await pool.query(query, [limit, offset,date]);
    // console.log(query)
    // console.log([limit, offset,...queryParams])
    const result = await pool.query(query, [...queryParams,limit, offset]);
    // return result;
    // 推算總頁數
    const totalItems = count; // 假設 req.count 中帶有總數(應該用jwt判斷)
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
