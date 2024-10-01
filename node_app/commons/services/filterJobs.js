const { pool } = require('../configs/dbConfig');
const {condGen}=require('../utils/jobCondGen')
const { getTime2ISO } = require('../utils/dateUtils');

// 批量處理查詢(有userid)
const filterJobs = async (conditions) => {
  try {
    const conditionStrings = conditions.map((cond) => {
      const { user_id } = cond;
      const { industries, job_info } = cond;
      const {conditionsArray,queryParams} = condGen(cond);
      return {
        user_id,
        conditionString: `(${conditionsArray.join(' AND ')})`,
        queryParams,
        sub: { industries, job_info },
      };
    });

    const results = await Promise.all(conditionStrings.map(async ({ user_id, conditionString,queryParams, sub}) => {
      // const query = `
      //   SELECT Count("industry") AS count
      //   FROM jobs
      //   WHERE ${conditionString}
      // `;
      
      //update_date是日期，故DATE操作的時區轉換無用
      const query = `
        WITH JobCounts AS (
          SELECT 
            COUNT(*) AS total_count,
            COUNT(CASE WHEN update_date = DATE(NOW() AT TIME ZONE 'UTC') THEN 1 END) AS today_count
          FROM jobs
          WHERE ${conditionString}
        )
        SELECT 
          total_count,
          today_count
        FROM JobCounts
      `;
      const result = await pool.query(query,queryParams);
      // return { user_id, count: result.rows[0].count, sub };
      return {
        user_id, count: result.rows[0].total_count, update: result.rows[0].today_count, sub, queryDate: getTime2ISO(new Date()),
      };
    }));

    return results;
  } catch (error) {
    console.error('Error querying jobs table:', error);
    return [];
  }
};

module.exports= { filterJobs }