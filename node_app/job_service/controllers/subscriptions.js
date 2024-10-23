const services = require('../services/subscriptions');
const userServices = require('../services/user');
const { client } = require('../configs/redisConfig'); // 載入 redis 客戶端的 async 方法

const validateUser = async (user_id) => {
  const existsUser = await userServices.existsUser(user_id);
  if (!existsUser) {
    await userServices.createUser(user_id);
  }
};

const getSubConditions = async (req, res, next) => {
  const { user_id } = req.params;
  try {
    validateUser(user_id);

    const result = await services.getSubConditions(user_id);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
};

const addSubConditions = async (req, res, next) => {
  try {
    const { user_id } = req.params;
    const { sub, exclude } = req.body.data;

    validateUser(user_id);

    await services.addSubConditions(user_id, sub, exclude);

    res.status(200).json('Insert successful');
  } catch (error) {
    console.log(error.message);
    next(error);
  }
};

const updateSubscribedEntitiesinRedis = async (user_id, client) => { // 更新redis
  const cacheKey = `${user_id}`;
  const data = await services.createSubscribedEntities(user_id);
  await client.setEx(cacheKey, 3600, JSON.stringify(data));
  console.log(data);
  return data;
};

// 如果太慢再考慮加入redis
const getSubscribedEntities = async (req, res, next) => {
  try {
    const { user_id } = req.params;

    validateUser(user_id);

    const data = await updateSubscribedEntitiesinRedis(user_id, client);

    return res.status(200).json({ message: 'Get successful', data });
  } catch (error) {
    next(error);
  }
};

const addSubscribedJob = async (req, res, next) => {
  try {
    const { user_id } = req.body;
    const { job_id } = req.params;
    console.log(user_id, job_id);

    validateUser(user_id);

    await services.addSubscribedJob(user_id, job_id);

    await updateSubscribedEntitiesinRedis(user_id, client);
    await services.updateJobChannel(job_id, user_id);

    return res.status(200).json('Insert successful');
  } catch (error) {
    next(error);
  }
};

const deleteSubscribedJob = async (req, res, next) => {
  try {
    const { user_id } = req.body;
    const { job_id } = req.params;
    console.log(user_id, job_id);
    // data 是否存在？
    validateUser(user_id);

    await services.deleteSubscribedJob(user_id, job_id);
    await updateSubscribedEntitiesinRedis(user_id, client);
    await services.deleteJobChannel(job_id, user_id);
    return res.status(200).json('Delete successful');
  } catch (error) {
    console.log(error.message);
    next(error);
  }
};

const addSubscribedCompany = async (req, res, next) => {
  try {
    const { user_id } = req.body;
    const { company_name } = req.params;
    // data 是否存在？
    validateUser(user_id);
    await services.addSubscribedCompany(user_id, company_name);
    await updateSubscribedEntitiesinRedis(user_id, client);
    await services.updateCompanyChannel(company_name, user_id);
    return res.status(200).json('Insert successful');
  } catch (error) {
    next(error);
  }
};

const deleteSubscribedCompany = async (req, res, next) => {
  try {
    const { user_id } = req.body;
    const { company_name } = req.params;
    validateUser(user_id);

    await services.deleteSubscribedCompany(user_id, company_name);
    await updateSubscribedEntitiesinRedis(user_id, client);
    await services.deleteCompanyChannel(company_name, user_id);

    return res.status(200).json('Delete successful');
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getSubConditions,
  addSubConditions,
  addSubscribedJob,
  deleteSubscribedJob,
  addSubscribedCompany,
  deleteSubscribedCompany,
  getSubscribedEntities,
};
