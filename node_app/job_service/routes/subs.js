const express = require('express');

const controller = require('../controllers/subs');

const router = express.Router();

// 思考api方法命名與使用便利性
router.get('/jobs_subscriptions/:user_id', controller.getJobSubs);
router.get('/id_subscriptions/:user_id', controller.getIdSubs);
router.post('/jobs_subscriptions', controller.addJobSubs);
router.post('/id_subscriptions', controller.postIdSubs);

// router.get('/subscriptions/conditions', controller.getSubscribedJobConditions');
// router.get('/subscriptions/entities', controller.getSubscribedJobEntities);
// router.post('/subscriptions/conditions', controller.addSubscribedJobConditions');
// router.post('/subscriptions/entities', controller.createOrUpdateSubscribedEntities);

module.exports = router;
