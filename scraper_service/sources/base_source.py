from abc import ABC, abstractmethod

class BaseSource(ABC):
    @abstractmethod
    def source_url(self, keyword, page):
        pass

    @abstractmethod
    def parse_source_job(self, base_url, soup=None, job=None):
        pass
