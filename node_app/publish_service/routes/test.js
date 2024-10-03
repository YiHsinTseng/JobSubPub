const express = require('express');
const { processBatchUserJobs, startCronJobs, stopCronJobs } = require('../services/pub');

const router = express.Router();

router.post('/trigger-push', async (req, res, next) => {
  try {
    // 調用 processBatchUserJobs 函數來處理並推送任務
    const result = await processBatchUserJobs();
    res.json({ status: 'success', message: 'Push triggered', data: result });
  } catch (error) {
    next(error);
  }
});

// 啟動定時任務
router.post('/start-routine', (req, res, next) => {
  try {
    startCronJobs();
    res.json({ status: 'success', message: 'Scheduled job started.' });
  } catch (error) {
    next(error);
  }
});

// 停止定時任務
router.post('/stop-routine', (req, res, next) => {
  try {
    stopCronJobs();//如果想要立刻停止在爬蟲迴圈要有檢查機制
    res.json({ status: 'success', message: 'Scheduled job stopped.' });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
