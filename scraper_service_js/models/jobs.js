class JobModel {
  constructor({
    title,
    companyName,
    industry,
    experience,
    description,
    salary,
    applicants,
    location,
    updateDate,
    recordTime,
    source,
    url,
    keywords,
    requirements,
    additionalConditions,
  }) {
    this.title = title;
    this.companyName = companyName;
    this.industry = industry;
    this.experience = experience;
    this.description = description;
    this.salary = salary;
    this.applicants = applicants;
    this.location = location;
    this.updateDate = updateDate;
    this.recordTime = recordTime;
    this.source = source;
    this.url = url;
    this.keywords = keywords;
    this.requirements = requirements;
    this.additionalConditions = additionalConditions;
  }

  toDict() {
    return {
      title: this.title,
      company_name: this.companyName,
      industry: this.industry,
      experience: this.experience,
      description: this.description,
      requirements: this.requirements, // Assuming job_info is JSONB and requirements is compatible
      additional_conditions: this.additionalConditions,
      salary: this.salary,
      people: this.applicants,
      location: this.location,
      update_date: this.updateDate,
      record_time: this.recordTime,
      source: this.source,
      keywords: this.keywords,
      url: this.url,
    };
  }
}

module.exports = JobModel;
