const express = require('express');

const router = express.Router();

const controller = require('../controllers/user-fav');

router.get('/:user_id/fav/:jobId/job-tag', controller.fetchJobIdTags);
router.post('/:user_id/fav', controller.filterJobsByTags);
router.post('/:user_id/fav/:jobId/job-tag', controller.upsertJobIdTags);

module.exports = router;
