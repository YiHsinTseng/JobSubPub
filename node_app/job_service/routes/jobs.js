const express = require('express');

const controller = require('../controllers/jobs');

const { authenticateJwt } = require('../middlewares/authenticate');

const router = express.Router();

router.post('/filterJobsBySub', authenticateJwt, controller.getJobs);

module.exports = router;
