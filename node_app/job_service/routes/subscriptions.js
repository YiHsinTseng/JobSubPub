const express = require('express');

const { cacheMiddleware } = require('../middlewares/redisCache');

const router = express.Router();

// 由於是自建外掛伺服器，所以安全以CORS以及IP為主，不做額外驗證

const controller = require('../controllers/subscriptions');

router.get('/users/:user_id/conditions_subscriptions', controller.getSubConditions);
router.post('/users/:user_id/conditions_subscriptions', controller.addSubConditions);
router.get('/users/:user_id/entities_subscriptions', cacheMiddleware, controller.getSubscribedEntities);
router.get('/users/:user_id/entities_subscriptions/job', controller.getSubscribedJobs);
router.post('/users/:user_id/entities_subscriptions/job/:job_id', controller.addSubscribedJob);
router.post('/users/:user_id/entities_subscriptions/company/:company_name', controller.addSubscribedCompany);
router.delete('/users/:user_id/entities_subscriptions/job/:job_id', controller.deleteSubscribedJob);
router.delete('/users/:user_id/entities_subscriptions/company/:company_name', controller.deleteSubscribedCompany);

module.exports = router;
