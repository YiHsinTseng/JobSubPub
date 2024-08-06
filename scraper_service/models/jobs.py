class JobModel:
    def __init__(self, title, company_name, industry, experience, description, salary, applicants, location, update_date, record_time, source, url,keywords, requirements, additional_conditions):
        self.title = title
        self.company_name = company_name
        self.industry = industry
        self.experience = experience
        self.description = description
        self.salary = salary
        self.applicants = applicants
        self.location = location
        self.update_date = update_date
        self.record_time = record_time
        self.source = source
        self.keywords = keywords
        self.url = url
        self.requirements = requirements
        self.additional_conditions = additional_conditions


    def to_dict(self):
            """
            Convert the Job instance to a general dictionary without FIELD_MAP.
            """
            return {
                'title': self.title,
                'company_name': self.company_name,
                'industry': self.industry,
                'experience': self.experience,
                'description': self.description,
                'salary': self.salary,
                'applicants': self.applicants,
                'location': self.location,
                'update_date': self.update_date,
                'record_time': self.record_time,
                'source': self.source,
                'keywords': self.keywords,
                'url': self.url,
                'requirements': self.requirements,
                'additional_conditions': self.additional_conditions
            }

    def to_dict_map(self): ##映射對前處理太浪費資源
            return {key: getattr(self, value) for key, value in self.FIELD_MAP.items()}