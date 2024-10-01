const { pool } = require('../configs/dbConfig');
// const { getSubscriptionConditions } = require('./subs');
const { condGen } =require('../utils/jobCondGen')
const { filterJobs } =require('./filterJobs')

// 回傳分頁值(沒有userid)
// 沒有排除條件


//硬編碼? 目前是傳給除非超過50筆，之後可以加入 getSubscriptionConditions
const getJobs = async (sub, exclude, count,dateString, limit = 50, offset = 0) => {
  // console.log(condition, count);

  const condition={...sub,...exclude}//TODO

  try {
  // 確保 conditions 是一個對象
    if (typeof condition !== 'object' || condition === null) {
      throw new Error('Invalid conditions format');
    }
    const {conditionsArray,queryParams} = condGen(condition);//聚合所有篩選與排除條件
    // console.log(conditionsArray)

    // 構建最終條件字符串
    const conditionString = conditionsArray.length > 0 ? `(${conditionsArray.join(' AND ')})` : 'TRUE'; // Default to TRUE if no conditions

     // 將日期參數加入 queryParams
     queryParams.push(dateString);

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
      AND update_date = $${queryParams.length}
      ORDER BY update_date DESC
      LIMIT $${queryParams.length + 1}  OFFSET $${queryParams.length + 2} 
    `;

    console.log(conditionString)
    //update_date是日期，故DATE操作的時區轉換無用
    //可能又更好的比較方式 update_date = ISO8601 可能不太好，但會做隱式轉換比較
    //NOTE 日期存成DATE但要轉換成UTC容易造成錯誤
    //NOTE 注意update_date原是TP，未轉換可能會被誤操作UTC，故目前update_date已轉成UTC時區儲存但是格式還是DATE沒有時區資訊。

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
  // getJobs, filterJobs, getSubscriptionConditions, condGen,
  getJobs, filterJobs, condGen,
};
