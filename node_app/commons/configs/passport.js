require('dotenv').config();

const passport = require('passport');
const JwtStrategy = require('passport-jwt').Strategy;
const { ExtractJwt } = require('passport-jwt');

const { pool } = require('./dbConfig');

const opts = {};
const extractJwtFromBody = (req) => req.body.authToken;// 假設 token 放在 body 的 'token' 屬性中
opts.jwtFromRequest = extractJwtFromBody,
opts.secretOrKey = process.env.PASSPORT_SECRET;

passport.use(
  new JwtStrategy(opts, async (jwt_payload, done) => {
    try {
      // 從數據庫中查找匹配的 user_id
      const query = 'SELECT * FROM job_subscriptions WHERE user_id = $1';
      const values = [jwt_payload.user_id];

      const result = await pool.query(query, values);

      if (result.rows.length > 0) {
        // 如果找到匹配的記錄，將其作為驗證成功的用戶對象返回
        const foundCustomer = result.rows[0];
        return done(null, foundCustomer); // req.user <= foundCustomer
      }

      return done(null, false); // 未找到匹配的記錄，驗證失敗
    } catch (e) {
      return done(e, false); // 處理錯誤情況
    }
  }),
);

module.exports = passport;
