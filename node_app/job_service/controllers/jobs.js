// const services = require('../services/mock_jobs');
const services = require('../services/jobs');
const { getDate } = require('../utils/dateUtils');

// 有沒有資格查 白名單或jwt
const getJobs = async (req, res, next) => {
  try {
    // const { user_id } = req.body; // 驗證要查表(代理請求使用?)
    const { count, sub ,queryDate } = req.body.data;
    const date = queryDate ? queryDate : getDate();
    const result = await services.getJobs(sub, count,date);// 這樣雖然快，但是可能會欺騙api(需要給定user_id嗎)
    res.json(result);
  } catch (error) {
    // console.error('Error querying jobs table:', error);
    // res.status(500).json({ error: 'Internal Server Error' });
    next(error);
  }
};

module.exports = {
  getJobs,
};
