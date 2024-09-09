const passport = require('../configs/passport');

const authenticateJwt = (req, res, next) => {
  const token = req.body.authToken;
  if (!token) {
    return res.status(401).send({ status: 'fail', message: 'Missing authToken' });
  }
  passport.authenticate('jwt', { session: false }, (err, user_id) => {
    // 如果出現錯誤，或者未找到用戶，返回 401 錯誤
    if (err || !user_id) {
      return res.status(401).send({ status: 'fail', message: 'Your authToken has expired or is invalid.' });
    }

    // 如果身份驗證成功，將用戶資訊存儲在 req.user 中，並繼續處理下一個中間件或路由處理程序
    req.user = user_id;
    next();
  })(req, res, next);
};

module.exports = { authenticateJwt };
