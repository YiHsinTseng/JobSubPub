const { pool } = require('../configs/dbConfig');
const { jobCondGen } = require('../utils/SQLParamsGen');

/**
 * 分頁查詢公開的工作列表。
 * 
 * 此函式根據使用者訂閱條件與排除條件，查詢公開工作資料表的特定頁數。
 * 
 * 使用者流程：
 * 1. 使用者首次點擊通知顯示頁面，傳送 page = 1 的 API 請求。
 * 2. 按下「下一頁」按鈕，頁數 `page` + 1，重新發送 API 請求。
 * 3. 若「上一頁」按鈕被按下，頁數減 1，重新發送 API 請求。

 * 
 * @param {number} count - 總筆數（若已知，否則自動計算）。
 * @param {object} sub - 訂閱條件。
 * @param {object} exclude - 排除條件。
 * @param {string} dateString - 日期條件，用於篩選更新日期。(原是TP DATE但已轉換UTC DATE格式) 
 * @param {number} limit - 每頁顯示的筆數。
 * @param {number} page - 查詢的頁數。
 */


const getPublishedJobsPaged = async (count, update, sub, exclude, dateString, page = 1, limit = 50) => {
  const condition = { ...sub, ...exclude };

  try {
    if (typeof condition !== 'object' || condition === null) {
      throw new Error('Invalid conditions format');
    }

    // 生成查詢化參數
    const { conditionString, queryParams } = jobCondGen(condition);// 聚合所有篩選與排除條件
    queryParams.push(dateString);

    const query = `
    SELECT *
    FROM jobs
    WHERE ${conditionString}
    AND update_date = $${queryParams.length}
    ORDER BY update_date DESC
    LIMIT $${queryParams.length + 1}  OFFSET $${queryParams.length + 2} 
    `;

    const offset = (page - 1) * limit;
    const result = await pool.query(query, [...queryParams, limit, offset]);

    const updateItems = update;
    const updateItemsPages = Math.ceil(updateItems / limit);
    const currentPage = page; // currentPage是指今天而非所有

    if (currentPage>updateItemsPages){
      throw new Error('今日更新已閱畢，是否需要查看舊資料');
    }
   
    // TODO 顯示符合條件的非今日職缺
    // 有需要排除今日的結果嗎？需要，查看更多（不要共用同一隻API，意味著開放自由查？）
    // 接續編號還是要自行編號?最聰明的做法是不要有編號避免更新資料庫造成前後不一致

    // 推算總頁數
    const totalItems = count; // TODO 假設 req.count 中帶有總數(應該用jwt判斷?)
    const totalPages = Math.ceil(totalItems / limit);

    return {
      currentPage,
      updateItemsPages,
      updateItems,
      totalItems,
      items: result.rows,
    };
  } catch (error) {
    console.error('Error querying jobs table:', error);
    throw new Error('Error querying jobs table: '+ error.message);
  }
};

module.exports = {
  getPublishedJobsPaged,
};
