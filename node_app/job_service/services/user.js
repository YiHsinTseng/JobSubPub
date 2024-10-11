const { pool } = require('../configs/dbConfig');

const createUser = async (user_id) => {
  try {
    const created_at = new Date();
    const result = await pool.query(
      'INSERT INTO users (user_id, created_at) VALUES ($1, $2) RETURNING *',
      [user_id, created_at],
    );

    return result.rows[0];
  } catch (error) {
    console.error('Error registering user:', error);
  }
};

const existsUser = async (user_id) => {
  try {
    const result = await pool.query(
      'SELECT * FROM users WHERE user_id = $1',
      [user_id],
    );
    return result.rows.length > 0; // Return true if user exists, otherwise false
  } catch (error) {
    console.error('Error checking if user exists:', error);
    throw error; // Rethrow the error for handling at a higher level
  }
};

module.exports = { createUser, existsUser };
