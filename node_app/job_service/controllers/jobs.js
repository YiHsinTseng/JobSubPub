// const services = require('../services/mock_jobs');
const services = require('../services/jobs');
const {getTime2ISO,isDateString,getcurrentDate } = require('../utils/dateUtils');

// 有沒有資格查 白名單或jwt
const getJobs = async (req, res, next) => {
  try {
    // const { user_id } = req.body; // 驗證要查表(代理請求使用?)
    const { count, sub ,exclude, queryDate:dateString } = req.body.data;
    // 皆使用 UTC 日期
    
    //TODO 日期格式可以是字串但最好是ISO用於驗證
    if(!isDateString(dateString)){
      return res.status(400).json({message:"時間格式必須是ISO8601"});
    }

    //其實不是今天authtoken也不會過
    let message
    
    //TODO 怎樣驗證比較好
    if (new Date(dateString)<getcurrentDate()){
      message ="not today notification"
      return res.status(400).json({message});//為何有回傳值
    }

    // const date = queryDate ? new Date(queryDate) : new Date(); 
    //因為爬蟲update時區是TP，不過record時區是UTC
    
    const result = await services.getJobs(sub,exclude, count, dateString);// 這樣雖然快，但是可能會欺騙api(需要給定user_id嗎)
   
    return res.status(200).json({message:"Success",result});
  } catch (error) {
    // console.error('Error querying jobs table:', error);
    // res.status(500).json({ error: 'Internal Server Error' });
    next(error);
  }
};

module.exports = {
  getJobs,
};
