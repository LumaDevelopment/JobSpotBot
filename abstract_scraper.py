"""
Abstract Scraper | Written by Joshua Sheldon

An abstract class. To use it, implement this class
in a file, and place that file in the "scrapers/"
directory. JobSpotBot will use that scraper as a
source of open jobs.
"""

# ---------- IMPORTS ----------

# Python Default Imports
from abc import ABC, abstractmethod

# ---------- CLASSES ----------


class AbstractScraper(ABC):
    @abstractmethod
    def scrape_open_jobs(self) -> set[tuple[str, str]]:
        """
        Scrapes all open jobs from a job board.
        :return: A set of open jobs represented by tuples. The
                 first element of each tuple is the job's name,
                 and the second element of each tuple is the
                 job's link.
        """
        pass
