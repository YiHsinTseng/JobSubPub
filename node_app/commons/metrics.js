const client = require('prom-client');

const { collectDefaultMetrics } = client;
const { Registry } = client;
const register = new Registry();
collectDefaultMetrics({ register });

// 設置一個簡單的 gauge 指標來測量目前的活躍請求數
const activeRequests = new client.Gauge({
  name: 'active_requests',
  help: 'Number of active requests',
});
register.registerMetric(activeRequests);

// 設置一個簡單的 counter 指標來測量請求數
const requestCounter = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'status_code'],
});
register.registerMetric(requestCounter);

// 設置一個簡單的 histogram 指標來測量請求處理時間
const requestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Histogram of HTTP request duration',
  labelNames: ['method', 'status_code'],
  buckets: [0.1, 0.5, 1, 2.5, 5, 10], // 可以自定義桶的大小
});
register.registerMetric(requestDuration);

// 中间件函数来处理计时
const monitoringMiddleware = (req, res, next) => {
  req.startTime = Date.now(); // 設置請求開始時間
  const end = requestDuration.startTimer({ method: req.method, status_code: 'pending' });
  activeRequests.inc();

  res.on('finish', () => {
    activeRequests.dec();
    const duration = (Date.now() - req.startTime) / 1000;
    if (!isNaN(duration)) {
      requestDuration.labels(req.method, res.statusCode).observe(duration);
    }
    requestCounter.labels(req.method, res.statusCode).inc();
  });

  next();
};

// Prometheus 指標處理函數
const prometheusMetricsHandler = async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
};

// 這個方法會返回 Registry 物件
module.exports = {
  register, activeRequests, requestCounter, requestDuration, monitoringMiddleware, prometheusMetricsHandler,
};
