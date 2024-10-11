const redis = require('redis');

const client = redis.createClient();

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
