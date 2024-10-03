const services = require('../services/jobs');
const {getTime2ISO,isDateString,getcurrentDate } = require('../utils/dateUtils');

const getTodayPublishedJobs = async (req, res, next) => {
  try {  
    // 限制過度搜尋？ ＝>authtoken先驗證身份id=>但是查詢內容就可以任意查

    // 只有驗證日期，其他PubbedInFo沒有驗證=>只能任意查找今日內容，舊通知過期
    // ? 如果舊通知要存本地擔心資料量太大？傳輸比較麻煩（討論資料傳輸）

    // date限縮範圍（今日通知）
    // sub ,exclude 主要搜尋條件
    // count,update(Count) 用來分頁（未實作）//應該先做不分頁版本
    const pubbedInFo=req.body.data;

    const { count, update, sub ,exclude, queryDate:dateString } = pubbedInFo

    if(!isDateString(dateString)){
      return res.status(400).json({message:"時間格式必須是ISO8601"});
    }

    let message
    if (new Date(dateString)<getcurrentDate()){
      message ="not today notification"
      return res.status(400).json({message});
    }
    const result = await services.getTodayPublishedJobsPaged(count,update,sub,exclude,dateString );

    return res.status(200).json({message:"Success",result});
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getTodayPublishedJobs,
};
