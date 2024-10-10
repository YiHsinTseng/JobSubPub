const passport = require('../configs/passport');

const authenticateJwt = (req, res, next) => {
  const token = req.body.authToken;
  if (!token) {
    return res.status(401).send({ status: 'fail', message: 'Missing authToken' });
  }
  passport.authenticate('jwt', { session: false }, (err, user) => {

    if (err || !user) {
      return res.status(401).send({ status: 'fail', message: 'Your authToken is invalid.' });
    }

    const{ user_info, iat_time ,exp_time } = user

    if (exp_time < new Date()) {
      message = 'Your authToken has expired';
      return res.status(400).json({status: 'fail',message });
    }
    
    req.user = user_info;
    req.jwtIat=iat_time
   
    next();
  })(req, res, next);
};

module.exports = { authenticateJwt };
