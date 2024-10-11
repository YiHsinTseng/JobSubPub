const services = require('../services/jobs');
const { getcurrentDate } = require('../utils/dateUtils');

const getTodayPublishedJobs = async (req, res, next) => {
  try {
    const iat_time = req.jwtIat;
    // 限制過度搜尋？ ＝>authtoken先驗證身份id=>但是查詢內容就可以任意查
    // 在jwt payload中加入限制驗證條件，不允許修改日期，不允許修改條件
    // =>日期其實可以用jwt驗，大小還可以接受
    // =>但儲存條件對JWT來說太佔用空間，使用redis地址？
    // 或是以redis來協助限制流量

    // 只有驗證日期，其他PubbedInFo沒有驗證=>只能任意查找今日內容，舊通知過期
    // ? 如果舊通知要存本地擔心資料量太大？傳輸比較麻煩（討論資料傳輸）
    // =>使用redis限流

    // date限縮範圍（今日通知）
    // sub ,exclude 主要搜尋條件
    // count,update(Count) 用來分頁（未實作）//應該先做不分頁版本

    const pubbedInFo = req.body.data;

    const {
      count, update, sub, exclude,
    } = pubbedInFo;

    // 以jwt創建日期為判斷
    let message;
    if (iat_time < getcurrentDate()) { // 今天凌晨
      message = 'not today notification';
      return res.status(400).json({ message });
    }

    const result = await services.getPublishedJobsPaged(count, update, sub, exclude, iat_time.toUTCString());

    return res.status(200).json({ message: 'Success', result });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getTodayPublishedJobs,
};
