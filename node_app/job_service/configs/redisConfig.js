const redis = require('redis');

const client = redis.createClient({
  url: 'redis://my-redis:6379',
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
