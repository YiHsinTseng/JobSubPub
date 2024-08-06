from controllers.jobs import JobController

def main():
    keyword = 'node.js'  # 修改為你需要的關鍵字
    job_controller = JobController()  # 創建 JobController 實例
    job_controller.search_and_save_jobs(keyword)  # 使用 JobController 進行操作

if __name__ == "__main__":
    main()
