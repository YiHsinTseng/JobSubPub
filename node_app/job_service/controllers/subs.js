const services = require('../services/subs');

const getJobSubs = async (req, res, next) => {
  const { user_id } = req.params;// 修改格式
  try {
    const result = await services.getJobSubs(user_id);// 這樣雖然快，但是可能會欺騙api
    // sub需要校驗資料格式
    res.status(200).json(result);
  } catch (error) {
    // console.error('Error adding job_subs table:', error);
    // res.status(500).json({ error: 'Internal Server Error' });
    console.log(error.message);
    next(error);
  }
};

const getIdSubs = async (req, res, next) => {
  const { user_id } = req.params;// 修改格式
  try {
    const result = await services.getIdSubs(user_id);// 這樣雖然快，但是可能會欺騙api
    // sub需要校驗資料格式
    res.status(200).json(result);
  } catch (error) {
    // console.error('Error adding job_subs table:', error);
    // res.status(500).json({ error: 'Internal Server Error' });
    console.log(error.message);
    next(error);
  }
};

const addJobSubs = async (req, res, next) => {
  // const { user_id, sub } = req.body.data;
  try {
    const { user_id } = req.body;// 修改格式
    const { sub } = req.body.data;
    await services.addJobSubs(user_id, sub);// 這樣雖然快，但是可能會欺騙api
    // sub需要校驗資料格式
    res.status(200).json('Insert successful');
  } catch (error) {
    // console.error('Error adding job_subs table:', error);
    // res.status(500).json({ error: 'Internal Server Error' });
    console.log(error.message);
    next(error);
  }
};

const postIdSubs = async (req, res, next) => {
  try {
    // const { user_id, sub } = req.body.data;
    const { user_id } = req.body; // 修改格式
    const { sub } = req.body.data;
    const { type } = req.body;
    // 可單增或批量
    if (!sub.job_ids && !sub.company_names) {
      res.status(400).json({ error: 'Bad Request Body' });
      return;
    }
    // if (sub.job_ids && sub.company_names) {
    //   res.status(400).json({ error: 'Bad Request Body' });
    //   return;
    // }

    if (type === 1) {
      await services.addIdSubs(user_id, sub);
      res.status(200).json('Insert successful');// 200才有訊息
    } else if (type === 2) {
      await services.deleteIdSubs(user_id, sub);
      res.status(200).json('delete successful');// 200才有訊息
    } else {
      res.status(400).json({ error: 'Bad Request Body' });
    }
  } catch (error) {
    next(error);
  }
};

module.exports = {
  addJobSubs, postIdSubs, getIdSubs, getJobSubs,
};
