const redis = require('redis');
require('dotenv').config(); // 加载环境变量

const redisUrl = process.env.REDIS_URL;

const client = redis.createClient({
  url: redisUrl,
});

// 確保 Redis 連線
(async () => {
  try {
    await client.connect();
    console.log('Connected to Redis server');
  } catch (err) {
    console.error('Redis connection failed:', err);
  }
})();

module.exports = { client };
