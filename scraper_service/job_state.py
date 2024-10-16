class JobState:
    def __init__(self):
        self.job_enabled = True  

    def start_job(self):
        self.job_enabled = True

    def stop_job(self):
        self.job_enabled = False

    def is_job_enabled(self):
        return self.job_enabled

# 創建全局的 JobState 實例
job_state = JobState()
