
const jobCondGen = (conditions) => {
  
  const { industries, job_info, exclude_job_title } = conditions; //因為不同資料有不同特性，所以暫採硬編碼 
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

  let excludedJobTitleCondition = '';
  if (exclude_job_title && exclude_job_title.length > 0) {
    excludedJobTitleCondition = `
    NOT EXISTS (
      SELECT 1
      FROM job_subscriptions 
      WHERE job_title ILIKE ANY(ARRAY[${exclude_job_title.map((_, i) => `$${i + industries.length + job_info.length + 1}`).join(', ')}])
    )
  `;//轉換成佔位符
    queryParams.push(...exclude_job_title.map(title => `%${title}%`)); //佔位符帶入模糊匹配
  }

  const conditionsArray = [];
  if (industryCondition) conditionsArray.push(industryCondition);
  if (job_infoCondition) conditionsArray.push(job_infoCondition);
  if (excludedJobTitleCondition) conditionsArray.push(excludedJobTitleCondition);

  const conditionString = conditionsArray.length > 0 ? `(${conditionsArray.join(' AND ')})` : 'TRUE';


  return {conditionString, queryParams};
};

module.exports={jobCondGen}