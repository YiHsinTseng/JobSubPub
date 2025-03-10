const userFavSerivce = require('../services/user-fav');

const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

const fetchJobIdTags =  asyncHandler(async (req, res, next) => { 
  const { user_id } = req.params;
  const { jobId } = req.params;

  const data = await userFavSerivce.fetchJobIdTags(jobId,user_id);
  return res.json({data});
})

const filterJobsByTags =  asyncHandler(async (req, res, next) => { 
  const { user_id } = req.params;
  const { tagNames } = req.body;
  const data = await userFavSerivce.filterJobsByTags(tagNames,user_id);
  return res.json({data});
})

const upsertJobIdTags =  asyncHandler(async (req, res, next) => {
  const { user_id } = req.params;
  const { jobId } = req.params;
  const { tagNames } = req.body;

  //直接用sql一次性操作
  const data = await userFavSerivce.upsertJobIdTags(tagNames,jobId,user_id);
  
  return res.json(data);
})

module.exports = {
  fetchJobIdTags,
  upsertJobIdTags,
  filterJobsByTags
};
