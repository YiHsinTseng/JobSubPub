const express = require('express');
const { job, scheduleJob } = require('./controllers/jobs');
const { startPrometheusServer } = require('./metrics');
const opRoutes = require('./routes/op'); // 運行時操作
const logger = require('./winston');

const app = express();
app.use(express.json());
// 運行時操作api
app.use('/', opRoutes);

const startApp = () => {
  const port = 5060;
  app.listen(port, () => {
    logger.info(`Express server running at http://localhost:${port}`, { source: 'server' });
  });
};

startApp();
startPrometheusServer();
// 初始化立刻爬蟲
job();
scheduleJob();
