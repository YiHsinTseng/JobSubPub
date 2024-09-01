// jobRoutes.js
const express = require('express');

const router = express.Router();
const { JOB_STATUS, REQUEST_COUNT } = require('../metrics');
const { job } = require('../controllers/jobs');

let jobRunning = true;

// Start job endpoint
router.post('/start_job', (req, res) => {
  jobRunning = true;
  JOB_STATUS.set(1);
  res.json({ status: 'Job started' });
});

// Stop job endpoint
router.post('/stop_job', (req, res) => {
  jobRunning = false;
  JOB_STATUS.set(0);
  res.json({ status: 'Job stopped' });
});

// Manually trigger job endpoint
router.post('/go_job', async (req, res) => {
  await job();
  REQUEST_COUNT.inc();
  res.json({ status: 'Job ongoing' });
});

module.exports = router;
