
const condGen = (cond) => {
  const { industries, job_info } = cond; // 給多一點選項？
  const queryParams = [];
  let industryCondition = '';
  if (industries && industries.length > 0) {
    // industryCondition = `industry IN (${industries.map((v) => `'${v}'`).join(',')})`;
    industryCondition = `industry IN (${industries.map((_, i) => `$${i + 1}`).join(',')})`;
    queryParams.push(...industries);
  }
  let job_infoCondition = '';
  if (job_info && job_info.length > 0) { // 修正判斷錯誤
    // job_infoCondition = `
    // EXISTS (
    //   SELECT 1
    //   FROM jsonb_array_elements(job_info) AS elem
    //   WHERE elem->>0 IN (${job_info.map((v) => `'${v}'`).join(',')})
    // )`
    job_infoCondition = `
    EXISTS (
      SELECT 1
      FROM jsonb_array_elements(job_info) AS elem
      WHERE elem->>0 IN (${job_info.map((_, i) => `$${i + industries.length + 1}`).join(',')})
    )
  `;
    queryParams.push(...job_info);
    ;
  }

  // 聚合所有條件
  const conditionsArray = [];
  if (industryCondition) conditionsArray.push(industryCondition);
  if (job_infoCondition) conditionsArray.push(job_infoCondition);

  return {conditionsArray, queryParams};
};

module.exports={condGen}