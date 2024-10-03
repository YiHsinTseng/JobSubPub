const { pool } = require('../configs/dbConfig');
const { jobCondGen } =require('../utils/SQLParamsGen')

//硬編碼? 目前是傳給除非超過50筆，之後可以加入 getSubscriptionConditions
// const { getSubscriptionConditions } = require('./subs');
// const { getUsersFilteredJobs } =require('./batchQuery')
//TODO 分頁式查詢下一頁功能(前端)
const getTodayPublishedJobsPaged = async (count, update,sub, exclude,dateString, limit = 50, page = 1) => {
  
  const condition={...sub,...exclude}
  
  try {
    if (typeof condition !== 'object' || condition === null) {
      throw new Error('Invalid conditions format');
    }

    //生成查詢化參數
    const {conditionString,queryParams} = jobCondGen(condition);//聚合所有篩選與排除條件
    console.log(conditionString)

    queryParams.push(dateString);

    //NOTE 日期存成DATE但要轉換成UTC容易造成錯誤
    //NOTE 注意update_date原是TP，未轉換可能會被誤操作UTC，故目前update_date已轉成UTC時區儲存但是格式還是DATE沒有時區資訊。
    

    const todayQuery = `
    SELECT *
    FROM jobs
    WHERE ${conditionString}
    AND update_date = $${queryParams.length}
    ORDER BY update_date DESC
    LIMIT $${queryParams.length + 1}  OFFSET $${queryParams.length + 2} 
    `;

    const offset = (page - 1) * limit;
    const todayResult = await pool.query(todayQuery, [...queryParams,limit, offset]);

    //TODO 今日可能不需要分頁？
    const totalUpdateItems = update; //TODO 假設 req.count 中帶有總數(應該用jwt判斷?)
    const totalUpdatePages = Math.ceil(totalUpdateItems / limit);
    const currentPage = page; // 直接使用 page
    //currentPage是指今天而非所有

    //TODO 有需要排除今日的結果嗎？需要，查看更多（不要共用同一隻API，意味著開放自由查？）
    // 推算總頁數
    const totalItems = count; //TODO 假設 req.count 中帶有總數(應該用jwt判斷?)
    const totalPages = Math.ceil(totalItems / limit);
    // const currentPage = Math.floor(offset / limit) + 1;

    return {
      currentPage,
      totalUpdatePages,
      totalUpdateItems,
      totalItems,
      items: todayResult.rows,
    };
  } catch (error) {
    console.error('Error querying jobs table:', error);
    throw new Error('Error querying jobs table');
  }
};

module.exports = {
  getTodayPublishedJobsPaged
};
