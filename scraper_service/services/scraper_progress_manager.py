import json
from datetime import datetime
from typing import Dict
import os


class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.state = {}
        # 自動建立資料夾（如果不存在）
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

    def load(self, current_date_string: str) -> Dict:
        try:
            with open(self.state_file, "r") as f:
                self.state = json.load(f)
            if self.state.get("date") != current_date_string:
                self.state = self._initialize(current_date_string)
        except FileNotFoundError:
            self.state = self._initialize(current_date_string)
        return self.state

    def save(self, state):
        self.state = state
        with open(self.state_file, "w") as f:
            json.dump(state, f, ensure_ascii=False)

    def _initialize(self, current_date_string: str) -> Dict:
        return {
            "date": current_date_string,
            "total_count": 0,
            "daily_inserted_count": 0,
            "last_page": None,
            "page": 0,
            "last_inserted_count": 0,
            "page_failed": False,
        }

    def log(self, log_file: str):
        with open(log_file, "a") as log:
            log.write(f"{datetime.now()}: {self.state_file} {json.dumps(self.state)}\n")
