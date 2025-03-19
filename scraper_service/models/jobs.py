from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json  # 使用 json 來處理 JSON 字串

"""專屬於資料庫欄位結構的轉換模型"""


# 因為我想要關聯直接用sql寫，用ORM感覺太肥大
class JobModel(BaseModel):
    # 映射邏輯跟ORM不同
    """外部輸入欄位名以title為主"""
    # 要對應SQL腳本順序，符合真實資料庫的命名
    # 所以外部如果是job_title就會出錯（js:title->pg:job_title）
    job_title: str = Field(..., alias="title")
    company_name: str = Field(..., alias="company_name")
    industry: str = Field(..., alias="industry")
    job_exp: str = Field(..., alias="experience")
    job_exp_year: Optional[int] = Field(
        None, ge=0, alias="experience_year"
    )  # 允許為 None 或 >= 0
    job_desc: str = Field(..., alias="description")
    job_info: List[str] = Field(..., alias="requirements")
    job_condition: Optional[str] = Field(
        ..., alias="additional_conditions"
    )  # Optional接受None值
    job_salary: Optional[str] = Field(None, alias="salary")  # Optional接受None值
    people: str = Field(0, alias="applicants")
    place: str = Field(..., alias="location")
    update_date: Optional[str] = Field(..., alias="update_date")  # Optional接受None值
    record_time: datetime = Field(..., alias="record_time")
    source: str = Field(..., alias="source")
    keywords: str = Field(..., alias="keywords")
    job_link: Optional[str] = Field(None, alias="url")  # Optional接受None值

    class Config:
        populate_by_name = True  # 允許直接使用 Python 變數名進行賦值
        from_attributes = True

    """用於資料庫參數化轉型"""

    def to_dict(self, use_alias=False):
        data = self.dict(by_alias=use_alias)
        # JSON轉成字串
        if isinstance(
            data["job_info"], list
        ):  # 使用 job_info (而非 requirements) 作為列表
            data["job_info"] = json.dumps(data["job_info"])
        return data
