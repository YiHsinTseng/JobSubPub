const express = require('express');
const { processJobs, startScheduledJob, stopScheduledJob } = require('../services/pub');

const router = express.Router();

router.post('/trigger-push', async (req, res, next) => {
  try {
    // 调用 processJobs 函数来处理并推送任务
    const result = await processJobs();
    res.json({ status: 'success', message: 'Push triggered', data: result });
  } catch (error) {
    next(error);
  }
});

// 启动定时任务
router.post('/start-routine', (req, res, next) => {
  try {
    startScheduledJob();
    res.json({ status: 'success', message: 'Scheduled job started.' });
  } catch (error) {
    next(error);
  }
});

// 停止定时任务
router.post('/stop-routine', (req, res, next) => {
  try {
    stopScheduledJob();
    res.json({ status: 'success', message: 'Scheduled job stopped.' });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
