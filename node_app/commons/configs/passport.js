require('dotenv').config();

const passport = require('passport');
const JwtStrategy = require('passport-jwt').Strategy;

const { pool } = require('./dbConfig');

const opts = {};
const extractJwtFromBody = (req) => req.body.authToken;// 假設 token 放在 body 的 'token' 屬性中
opts.jwtFromRequest = extractJwtFromBody,
opts.secretOrKey = process.env.PASSPORT_SECRET;

passport.use(
  new JwtStrategy(opts, async (jwt_payload, done) => {
    try {
    
      // 以query驗證為主
     
      const query = 'SELECT * FROM job_subscriptions WHERE user_id = $1';
      const values = [jwt_payload.user_id];
      const result = await pool.query(query, values);

      const jwtExp=jwt_payload.exp
      const expDateUTC=new Date(jwtExp * 1000);

      const jwtIat=jwt_payload.iat
      const iatDateUTC=new Date(jwtIat * 1000);

      if (result.rows.length > 0) {
        const foundCustomer = result.rows[0];
        const user={ user_info: foundCustomer, iat_time: iatDateUTC ,exp_time: expDateUTC }
        return done(null, user); // req.user <= foundCustomer
      }

      return done(null, false); // 未找到匹配的記錄，驗證失敗
    } catch (e) {
      return done(e, false); // 處理錯誤情況
    }
  }),
);

module.exports = passport;
