const express = require('express');
const prometheus = require('prom-client');

// 創建一個新的 Express 應用來處理 Prometheus 指標
const prometheusApp = express();

// 定義 Prometheus metrics
const REQUEST_COUNT = new prometheus.Counter({
  name: 'express_app_requests_total',
  help: 'Total number of requests',
});

const JOB_STATUS = new prometheus.Gauge({
  name: 'job_status',
  help: 'Whether the job is running (1) or stopped (0)',
});

const JOB_DURATION = new prometheus.Summary({
  name: 'job_duration_seconds',
  help: 'Time spent processing job',
});

// 自動收集預設的 Prometheus metrics
prometheus.collectDefaultMetrics();

prometheusApp.get('/metrics', async (req, res) => {
  try {
    res.setHeader('Content-Type', prometheus.register.contentType);
    // 獲取 metrics 並返回結果
    const metrics = await prometheus.register.metrics();
    res.end(metrics);
  } catch (error) {
    res.status(500).send('Error generating metrics');
  }
});

// Function to start Prometheus metrics server
const startPrometheusServer = () => {
  const prometheusPort = 8001;
  prometheusApp.listen(prometheusPort, () => {
    console.log(`Prometheus metrics available at http://localhost:${prometheusPort}/metrics`);
  });
};

module.exports = {
  REQUEST_COUNT,
  JOB_STATUS,
  JOB_DURATION,
  prometheus,
  startPrometheusServer,
};
