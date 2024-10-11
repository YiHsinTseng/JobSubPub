const { client } = require('../configs/redisConfig'); // 載入 redis 客戶端的 async 方法

const cacheMiddleware = async (req, res, next) => {
  const userId = req.params.user_id;
  const cacheKey = `${userId}`;// 必須是string

  try {
    const data = await client.get(cacheKey);
    // console.log('Fetched from Redis:', data);
    if (data) {
      console.log('Fetched from Redis:', data);
      return res.status(200).json({ message: 'Get successful', data: JSON.parse(data) });
    }
    console.log('Fetched from DB');
    next();
  } catch (err) {
    console.error('Error retrieving data from cache', err);
    return res.status(500).send('Error retrieving data from cache');
  }
};

module.exports = { cacheMiddleware };
