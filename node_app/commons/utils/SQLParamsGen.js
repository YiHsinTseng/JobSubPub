
const jobCondGen = (conditions) => {
  
  const { industries, job_info,job_exp_range, exclude_job_title } = conditions; //因為不同資料有不同特性，所以暫採硬編碼 
  const queryParams = [];

  let industryCondition = '';
  if (industries && industries.length > 0) {
    industryCondition = `industry ILIKE ANY (ARRAY[${industries.map((_, i) => `$${i + 1}`).join(',')}])`;//轉換成佔位符
    queryParams.push(...industries.map(industry => `%${industry}%`)); //佔位符帶入模糊匹配
  }

  let job_infoCondition = '';
  if (job_info && job_info.length > 0) { 
  //改成部分模糊匹配(%%) 不區分大小寫(ILIKE) 
  job_infoCondition = `
  EXISTS (
    SELECT 1
    FROM jsonb_array_elements(job_info) AS elem
    WHERE elem->>0 ILIKE ANY (ARRAY[${job_info.map((_, i) => `$${i + industries.length + 1}`).join(',')}])
 )
`;//轉換成佔位符
  //佔位符帶入模糊匹配
    queryParams.push(...job_info.map(info => `%${info}%`));//佔位符帶入模糊匹配
    ;
  }


  // 年資條件範圍的判斷
  let job_exp_rangeCondition = "";

  if (job_exp_range === null || (Array.isArray(job_exp_range) && job_exp_range.length === 0)) {
    job_exp_rangeCondition = ''; // 不生成條件
    //跳過初始化欄位
  } else {
    console.log("有推")
    console.log("job_exp_range",job_exp_range)//因為批量寫入沒用::json所以數字元素會自動轉型字串
    let { minExp, maxExp } = job_exp_range;
    if(!(minExp===null&&maxExp===null)){
      console.log("有算")
      let expConditions = [];
      // 當 minExp 是 NaN 且 maxExp 已定義時，設置 minExp 為 0
      if (minExp===null && maxExp !== undefined) {
        minExp = 0; // 默認為 0
      }

      // 當 maxExp 是 NaN 且 minExp 已定義時，設置 maxExp 為 Infinity
      if (maxExp===null && minExp !== undefined) {
        maxExp = 99; // 用真的無限大會變NaN
      }
      console.log("job_exp_range算後",{minExp,maxExp})

      // 取下限
      if (minExp !== undefined && !isNaN(minExp)) {
        expConditions.push(`job_exp_year >= $${queryParams.length + 1}`);
        queryParams.push(parseInt(minExp));
      }

      // 取上限
      if (maxExp !== undefined && !isNaN(maxExp)) {
        expConditions.push(`job_exp_year <= $${queryParams.length + 1}`);
        queryParams.push(parseInt(maxExp));
      }

      if (expConditions.length > 0) {
        job_exp_rangeCondition = `(${expConditions.join(" AND ")})`;
      }
      console.log(expConditions)
      console.log(queryParams)
    }
  }

  let excludedJobTitleCondition = '';
  if (exclude_job_title && exclude_job_title.length > 0) {
    excludedJobTitleCondition = `
    NOT EXISTS (
      SELECT 1
      FROM job_subscriptions 
      WHERE job_title ILIKE ANY(ARRAY[${exclude_job_title.map((_, i) => `$${i + queryParams.length + 1}`).join(', ')}])
    )
  `;//轉換成佔位符
    queryParams.push(...exclude_job_title.map(title => `%${title}%`)); //佔位符帶入模糊匹配
  }

  const conditionsArray = [];
  if (industryCondition) conditionsArray.push(industryCondition);
  if (job_infoCondition) conditionsArray.push(job_infoCondition);
  if (job_exp_rangeCondition) conditionsArray.push(job_exp_rangeCondition);
  if (excludedJobTitleCondition) conditionsArray.push(excludedJobTitleCondition);

  const conditionString = conditionsArray.length > 0 ? `(${conditionsArray.join(' AND ')})` : 'TRUE';


  return {conditionString, queryParams};
};

module.exports={jobCondGen}