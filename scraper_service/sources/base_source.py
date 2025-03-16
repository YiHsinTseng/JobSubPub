from abc import ABC, abstractmethod


class BaseSource(ABC):
    @abstractmethod
    def make_query_url(self, keyword, page):
        pass

    @abstractmethod
    def parse_job_list_page(self, keyword, soup):
        pass

    @abstractmethod
    def parse_job_detail(self, keyword, job):
        pass
