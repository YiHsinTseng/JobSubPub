const express = require('express');

const { cacheMiddleware } = require('../middlewares/redisCache');

const router = express.Router();

// 訂閱沒驗證，把user_id當密碼

const controllerx = require('../controllers/subscriptions');

router.get('/conditions_subscriptions/:user_id', controllerx.getSubConditions);
router.post('/conditions_subscriptions/:user_id', controllerx.addSubConditions);

router.get('/entities_subscriptions/:user_id', cacheMiddleware, controllerx.getSubscribedEntities);
router.post('/entities_subscriptions/job/:job_id', controllerx.addSubscribedJob);
router.post('/entities_subscriptions/company/:company_name', controllerx.addSubscribedCompany);
router.delete('/entities_subscriptions/job/:job_id', controllerx.deleteSubscribedJob);
router.delete('/entities_subscriptions/company/:company_name', controllerx.deleteSubscribedCompany);

module.exports = router;
