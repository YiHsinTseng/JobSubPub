const { pool } = require('../configs/dbConfig');

//TODO 存到user prefer 不用另外使用api，整合到fetch fav/sub job，但是目前就先分開來

const filterJobsByTags = async (tagNames,user_id) => {
  try {
    // const tags = Array.isArray(tagNames) ? tagNames : [tagNames]; // 確保變成陣列

    //篩選出來的Job包含其他tagNames
    const query = `
      SELECT 
      js.*,
      COALESCE(json_agg(j.tag_name) FILTER (WHERE j.tag_name IS NOT NULL), '[]') AS job_tags
    FROM 
      subscriptions_jobs sj
    LEFT JOIN 
      subscriptions_jobs_tags s ON s.job_id = sj.job_id
    LEFT JOIN 
      jobs js ON js.job_id = sj.job_id::integer
    LEFT JOIN 
      job_tags j ON s.tag_id = j.id
    WHERE 
      sj.user_id = $2
      AND EXISTS (
        SELECT 1
        FROM job_tags jt
        JOIN subscriptions_jobs_tags sjt ON sjt.tag_id = jt.id
        WHERE sjt.job_id = sj.job_id
        AND jt.tag_name = ANY($1::text[])
        )
    GROUP BY 
      sj.user_id, js.job_id, sj.job_id;
    `

    const result = await pool.query(query, [tagNames,user_id]);
    return result.rows;

  } catch (err) {
    console.error('❌ 查詢訂閱標籤時出錯:', err);
    throw err;
  }
};

const fetchJobIdTags = async (jobId,user_id) => {
  try {
    const query = `
      SELECT s.job_id, json_agg(j.tag_name) as job_tags
      FROM subscriptions_jobs_tags s
      JOIN job_tags j ON s.tag_id = j.id
      WHERE s.user_id = $2
      AND  s.job_id=$1
      GROUP BY s.job_id;
    `;
    const res = await pool.query(query,[jobId,user_id]);
    return res.rows[0]?.job_tags||[]//這裡想好的話就能簡化前端操作邏輯
  } catch (err) {
    console.error('❌ 查詢訂閱標籤時出錯:', err);
    throw err;
  }
};

const upsertTagIds = async (tagNames) => {

  const selectQuery = `
    SELECT id, tag_name FROM job_tags WHERE tag_name = ANY($1::text[])
  `;
  const res = await pool.query(selectQuery, [tagNames]);
  const existingTags = res.rows.reduce((acc, row) => {
    acc[row.tag_name] = row.id;
    return acc;
  }, {});

  const insertTags = tagNames.filter(tag => !existingTags[tag]);

  if (insertTags.length > 0) {
    const values = insertTags.map((_, index) => `($${index + 1})`).join(", ");
    const insertQuery = `
      INSERT INTO job_tags (tag_name)
      VALUES ${values}
      RETURNING id, tag_name
    `;
    const insertRes = await pool.query(insertQuery, insertTags);

    insertRes.rows.forEach(row => {
      existingTags[row.tag_name] = row.id;
    });
  }
  return tagNames.map(tag => existingTags[tag]);
};


const upsertJobIdTags = async (tagNames, jobId,user_id) => {
  try {
    const currentTagsResult = await pool.query(
      `SELECT tag_id FROM subscriptions_jobs_tags WHERE job_id = $1`,
      [jobId]
    );
    const currentTagIds = currentTagsResult.rows.map(row => row.tag_id);
    const tagIds = await upsertTagIds(tagNames); // 回傳 array of tagIds

    const tagsToAdd = tagIds.filter(tagId => !currentTagIds.includes(tagId));
    const tagsToRemove = currentTagIds.filter(tagId => !tagIds.includes(tagId));

    if (tagsToAdd.length > 0) {
      const addValues = tagsToAdd.map((_, index) => 
        `($1,$2, $${index + 3})`
      ).join(", ");
      //問題在這裡
      const addQueryParams = [user_id,String(jobId), ...tagsToAdd];
      const addQuery = `
        INSERT INTO subscriptions_jobs_tags (user_id, job_id, tag_id)
        VALUES ${addValues}
        ON CONFLICT (user_id, job_id, tag_id) DO NOTHING;
      `;
      await pool.query(addQuery, addQueryParams);
      console.log(`✅ 標籤 "${tagsToAdd.join(", ")}" 插入成功或已存在.`);
    }
    if (tagsToRemove.length > 0) {
      const removeQuery = `
        DELETE FROM subscriptions_jobs_tags
        WHERE job_id = $1 AND tag_id = ANY($2);
      `;
      await pool.query(removeQuery, [jobId, tagsToRemove]);
      console.log(`✅ 標籤 "${tagsToRemove.join(", ")}" 已移除.`);
    }
    return { added: tagsToAdd, removed: tagsToRemove };
  } catch (err) {
    console.error('❌ 插入或刪除標籤時出錯:', err);
    throw err;
  }
};


module.exports = {
  fetchJobIdTags,
  filterJobsByTags,
  upsertTagIds,
  upsertJobIdTags,
};
