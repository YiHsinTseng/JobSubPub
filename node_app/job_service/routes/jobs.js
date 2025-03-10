const express = require('express');

const controller = require('../controllers/jobs');

const { authenticateJwt } = require('../middlewares/authenticate');

const router = express.Router();

// get不能攜帶json資訊，改post就不restful
// 限制資訊保質期與具token身分驗證的查詢API
router.post('/jobs/published', authenticateJwt, controller.getTodayPublishedJobs);

module.exports = router;
