const { pool } = require('../configs/dbConfig');
const {jobCondGen}=require('../utils/SQLParamsGen')
const { getTime2ISO } = require('../utils/dateUtils');


const getUsersSubscriptionConditionsPaginated = async (offset = 0, limit = 100) => {
  try {
    const query = `
      SELECT user_id, industries, job_info, exclude_job_title 
      FROM job_subscriptions 
      ORDER BY id 
      LIMIT $1 OFFSET $2
    `;
    const result = await pool.query(query, [limit, offset]);
    return result.rows.map((row) => ({
      user_id: row.user_id,
      industries: row.industries,
      job_info: row.job_info,
      exclude_job_title: row.exclude_job_title,
    }));
  } catch (error) {
    console.error('Error querying job_subscriptions table:', error);
    return [];
  }
};

const getUsersFilteredJobs = async (usersConditions) => {
  try {
    const usersConditionStrings = usersConditions.map((userConditions) => {
      const { user_id } = userConditions;
      const { industries, job_info, exclude_job_title } = userConditions;
      const { conditionString ,queryParams} = jobCondGen(userConditions);
      return {
        user_id,
        conditionString,
        queryParams,
        sub: { industries, job_info },
        exclude: {exclude_job_title }
      };
    });

    const results = await Promise.all(
      usersConditionStrings.map(
        async ({ user_id, conditionString,queryParams, sub, exclude }) => {    
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
          return {
            user_id, 
            count: result.rows[0].total_count,
            update: result.rows[0].today_count, 
            sub,
            exclude, 
            queryDate: getTime2ISO(new Date()),
          };
        }
      )
    );

    return results;

  } catch (error) {
    console.error('Error querying jobs table:', error);
    return [];
  }
};

module.exports= { getUsersSubscriptionConditionsPaginated, getUsersFilteredJobs }