
const jobCondGen = (conditions) => {
  
  const { industries, job_info, exclude_job_title } = conditions; //因為不同資料有不同特性，所以暫採硬編碼 
  const queryParams = [];

  let industryCondition = '';
  if (industries && industries.length > 0) {
    industryCondition = `industry IN (${industries.map((_, i) => `$${i + 1}`).join(',')})`;
    queryParams.push(...industries);
  }

  let job_infoCondition = '';
  if (job_info && job_info.length > 0) { 
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

  let excludedJobTitleCondition = '';
  if (exclude_job_title && exclude_job_title.length > 0) {
    excludedJobTitleCondition = `
    NOT EXISTS (
      SELECT 1
      FROM job_subscriptions 
      WHERE job_title LIKE ANY(ARRAY[${exclude_job_title.map((_, i) => `$${i + industries.length + job_info.length + 1}`).join(', ')}])
    )
  `;
    queryParams.push(...exclude_job_title.map(title => `%${title}%`));
  }

  const conditionsArray = [];
  if (industryCondition) conditionsArray.push(industryCondition);
  if (job_infoCondition) conditionsArray.push(job_infoCondition);
  if (excludedJobTitleCondition) conditionsArray.push(excludedJobTitleCondition);

  const conditionString = conditionsArray.length > 0 ? `(${conditionsArray.join(' AND ')})` : 'TRUE';


  return {conditionString, queryParams};
};

module.exports={jobCondGen}